from __future__ import annotations

"""Input Integrity Guard (IIG) del sistema Catálogo para T_Versiones.

Este módulo implementa la validación estructural previa a la validación semántica
(DVL) dentro del flujo oficial del sistema:

    SCRAPER -> DICT LIMPIO -> IIG -> DVL -> VALIDACIÓN DE LOTE -> INGESTIÓN

Responsabilidades del IIG_Catalogo:
- validar que el registro respeta el contrato formal de datos
- validar claves extra y claves requeridas ausentes
- validar tipos primitivos y formatos básicos de date/datetime
- validar la presencia de campos mínimos operativos
- detectar densidad alta de valores nulos o vacíos
- generar resultados estructurados por registro y por lote

Fuera de alcance explícito:
- no normaliza
- no corrige
- no infiere
- no modifica el input

El dict original siempre se devuelve intacto dentro de la estructura de salida.
"""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


@dataclass(frozen=True)
class ValidationMessage:
    """Mensaje estructurado emitido durante una validación."""

    code: str
    level: str  # info | warning | error | critical
    field: Optional[str]
    message: str
    expected: Optional[Any] = None
    received: Optional[Any] = None


@dataclass(frozen=True)
class RecordFlags:
    """Banderas de estado resumidas para un registro validado."""

    has_errors: bool = False
    has_critical: bool = False
    schema_valid: bool = True
    types_valid: bool = True
    minimum_fields_valid: bool = True
    null_density_warning: bool = False
    low_technical_content_warning: bool = False
    should_block: bool = False


@dataclass(frozen=True)
class RecordValidationResult:
    """Resultado completo de validación para un único registro."""

    original_record: Dict[str, Any]
    is_valid: bool
    flags: RecordFlags
    errors: List[ValidationMessage] = field(default_factory=list)
    warnings: List[ValidationMessage] = field(default_factory=list)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BatchValidationResult:
    """Resultado agregado de validación para un lote de registros."""

    total_records: int
    valid_records: int
    records_with_errors: int
    critical_records: int
    error_rate: float
    critical_rate: float
    avg_null_percentage: float
    anomaly_flags: List[str]
    error_summary: Dict[str, int]
    warning_summary: Dict[str, int]
    record_results: List[RecordValidationResult]


class IIG_Catalogo:
    """Guardián estructural del contrato de datos del catálogo.

    El IIG valida estructura, tipos, mínimos operativos y métricas básicas de lote
    sin alterar nunca el contenido del registro.
    """

    ALLOWED_LEVELS = {"info", "warning", "error", "critical"}
    SUPPORTED_TYPES = {"string", "integer", "number", "boolean", "date", "datetime"}

    def __init__(
        self,
        contract_path: str | Path,
        mode: str = "observacion",
        null_warning_threshold: float = 0.70,
        null_critical_threshold: float = 0.90,
        minimum_technical_fields: Optional[Sequence[str]] = None,
        minimum_technical_non_null: int = 3,
        batch_error_warning_threshold: float = 0.15,
        batch_error_critical_threshold: float = 0.35,
    ) -> None:
        """Inicializa el IIG a partir de un contrato JSON.

        Args:
            contract_path: ruta al contrato formal JSON.
            mode: "observacion" o "estricto".
            null_warning_threshold: umbral para warning de densidad de nulos.
            null_critical_threshold: umbral para nivel crítico de densidad de nulos.
            minimum_technical_fields: lista de campos técnicos usada para medir
                contenido técnico mínimo.
            minimum_technical_non_null: mínimo de campos técnicos no nulos para no
                marcar el registro con warning.
            batch_error_warning_threshold: umbral de warning para tasa de error de lote.
            batch_error_critical_threshold: umbral crítico para tasa de error de lote.
        """
        self.contract_path = Path(contract_path)
        self.mode = mode
        self.null_warning_threshold = null_warning_threshold
        self.null_critical_threshold = null_critical_threshold
        self.minimum_technical_non_null = minimum_technical_non_null
        self.batch_error_warning_threshold = batch_error_warning_threshold
        self.batch_error_critical_threshold = batch_error_critical_threshold

        self.contract = self._load_contract(self.contract_path)
        self.fields: Dict[str, Dict[str, Any]] = self.contract["fields"]
        self.required_minimum_fields: List[str] = list(self.contract["required_minimum_fields"])
        self.required_fields: List[str] = [
            field_name
            for field_name, meta in self.fields.items()
            if meta.get("required", False) is True
        ]
        self.allowed_keys = set(self.fields.keys())

        self.minimum_technical_fields = list(minimum_technical_fields) if minimum_technical_fields else [
            "power_cv",
            "power_bhp",
            "fuel_type",
            "engine_name",
            "engine_displacement_cc",
            "max_power_cv",
            "max_torque_nm",
            "top_speed_kmh",
            "acceleration_0_100_s",
            "gearbox_type",
            "length_mm",
            "kerb_weight_kg",
            "fuel_tank_l",
        ]

    def validate_record(self, record: Dict[str, Any]) -> RecordValidationResult:
        """Valida un único registro del catálogo."""
        if not isinstance(record, dict):
            msg = ValidationMessage(
                code="record_not_dict",
                level="critical",
                field=None,
                message="El input recibido no es un dict",
                expected="dict",
                received=type(record).__name__,
            )
            flags = RecordFlags(
                has_errors=True,
                has_critical=True,
                schema_valid=False,
                types_valid=False,
                minimum_fields_valid=False,
                should_block=True,
            )
            return RecordValidationResult(
                original_record=record if isinstance(record, dict) else {"_raw": record},
                is_valid=False,
                flags=flags,
                errors=[msg],
                warnings=[],
                logs=[self._to_log(msg)],
                metrics={},
            )

        errors: List[ValidationMessage] = []
        warnings: List[ValidationMessage] = []

        errors.extend(self._validate_structure(record))
        errors.extend(self._validate_required_fields(record))
        errors.extend(self._validate_minimum_fields(record))
        type_errors, type_warnings = self._validate_types(record)
        errors.extend(type_errors)
        warnings.extend(type_warnings)

        null_messages, null_warning_flag, _, null_percentage = self._validate_null_density(record)
        warnings.extend([m for m in null_messages if m.level == "warning"])
        errors.extend([m for m in null_messages if m.level in {"error", "critical"}])

        technical_messages, low_technical_content = self._validate_technical_minimum(record)
        warnings.extend(technical_messages)

        has_errors = len(errors) > 0
        has_critical = any(m.level == "critical" for m in errors)
        schema_valid = not any(
            m.code in {
                "extra_keys",
                "missing_required_keys",
                "missing_minimum_fields",
                "non_nullable_null",
                "empty_required_string",
            }
            for m in errors
        )
        types_valid = not any(m.code in {"invalid_type", "invalid_date", "invalid_datetime"} for m in errors)
        minimum_fields_valid = not any(m.code == "missing_minimum_fields" for m in errors)

        should_block = has_critical
        if self.mode == "estricto" and has_errors:
            should_block = True

        flags = RecordFlags(
            has_errors=has_errors,
            has_critical=has_critical,
            schema_valid=schema_valid,
            types_valid=types_valid,
            minimum_fields_valid=minimum_fields_valid,
            null_density_warning=null_warning_flag,
            low_technical_content_warning=low_technical_content,
            should_block=should_block,
        )

        logs = [self._to_log(msg) for msg in [*errors, *warnings]]
        metrics = {
            "field_count_received": len(record),
            "field_count_contract": len(self.fields),
            "null_percentage": round(null_percentage, 4),
            "non_null_technical_fields": self._count_non_null_technical_fields(record),
            "mode": self.mode,
        }

        return RecordValidationResult(
            original_record=record,
            is_valid=not has_errors,
            flags=flags,
            errors=errors,
            warnings=warnings,
            logs=logs,
            metrics=metrics,
        )

    def validate_batch(self, records: Sequence[Dict[str, Any]]) -> BatchValidationResult:
        """Valida un lote de registros y devuelve métricas agregadas."""
        results = [self.validate_record(record) for record in records]

        total_records = len(results)
        valid_records = sum(1 for result in results if result.is_valid)
        records_with_errors = sum(1 for result in results if result.flags.has_errors)
        critical_records = sum(1 for result in results if result.flags.has_critical)

        error_rate = (records_with_errors / total_records) if total_records else 0.0
        critical_rate = (critical_records / total_records) if total_records else 0.0
        avg_null_percentage = (
            sum(result.metrics.get("null_percentage", 0.0) for result in results) / total_records
            if total_records
            else 0.0
        )

        error_summary: Dict[str, int] = {}
        warning_summary: Dict[str, int] = {}

        for result in results:
            for error in result.errors:
                error_summary[error.code] = error_summary.get(error.code, 0) + 1
            for warning in result.warnings:
                warning_summary[warning.code] = warning_summary.get(warning.code, 0) + 1

        anomaly_flags: List[str] = []
        if total_records == 0:
            anomaly_flags.append("empty_batch")
        if error_rate >= self.batch_error_warning_threshold:
            anomaly_flags.append("high_error_rate")
        if error_rate >= self.batch_error_critical_threshold:
            anomaly_flags.append("critical_error_rate")
        if avg_null_percentage >= self.null_warning_threshold:
            anomaly_flags.append("high_null_density_batch")
        if critical_rate > 0:
            anomaly_flags.append("critical_records_present")

        return BatchValidationResult(
            total_records=total_records,
            valid_records=valid_records,
            records_with_errors=records_with_errors,
            critical_records=critical_records,
            error_rate=round(error_rate, 4),
            critical_rate=round(critical_rate, 4),
            avg_null_percentage=round(avg_null_percentage, 4),
            anomaly_flags=anomaly_flags,
            error_summary=error_summary,
            warning_summary=warning_summary,
            record_results=results,
        )

    def _load_contract(self, path: Path) -> Dict[str, Any]:
        if not path.exists():
            raise FileNotFoundError(f"Contrato no encontrado: {path}")

        with path.open("r", encoding="utf-8") as file_handle:
            contract = json.load(file_handle)

        if "fields" not in contract or "required_minimum_fields" not in contract:
            raise ValueError("Contrato inválido: faltan 'fields' o 'required_minimum_fields'")

        for field_name, meta in contract["fields"].items():
            expected_type = meta.get("type")
            if expected_type not in self.SUPPORTED_TYPES:
                raise ValueError(
                    f"Tipo no soportado en contrato para '{field_name}': {expected_type}"
                )

        return contract

    def _validate_structure(self, record: Dict[str, Any]) -> List[ValidationMessage]:
        extra_keys = sorted(set(record.keys()) - self.allowed_keys)
        if not extra_keys:
            return []

        return [
            ValidationMessage(
                code="extra_keys",
                level="critical",
                field=None,
                message="El registro contiene claves no definidas en el contrato",
                expected=sorted(self.allowed_keys),
                received=extra_keys,
            )
        ]

    def _validate_required_fields(self, record: Dict[str, Any]) -> List[ValidationMessage]:
        messages: List[ValidationMessage] = []

        missing_required = [field_name for field_name in self.required_fields if field_name not in record]
        if missing_required:
            messages.append(
                ValidationMessage(
                    code="missing_required_keys",
                    level="critical",
                    field=None,
                    message="Faltan claves requeridas por contrato",
                    expected=self.required_fields,
                    received=missing_required,
                )
            )

        for field_name in self.required_fields:
            if field_name not in record:
                continue

            value = record[field_name]
            meta = self.fields[field_name]
            if value is None and meta.get("nullable", True) is False:
                messages.append(
                    ValidationMessage(
                        code="non_nullable_null",
                        level="critical",
                        field=field_name,
                        message="Campo no nullable recibido como NULL",
                        expected="non-null",
                        received=None,
                    )
                )

            if meta.get("type") == "string" and isinstance(value, str) and value.strip() == "":
                messages.append(
                    ValidationMessage(
                        code="empty_required_string",
                        level="error",
                        field=field_name,
                        message="Campo string requerido recibido vacío",
                        expected="non-empty string",
                        received=value,
                    )
                )

        return messages

    def _validate_minimum_fields(self, record: Dict[str, Any]) -> List[ValidationMessage]:
        missing: List[str] = []
        for field_name in self.required_minimum_fields:
            if field_name not in record:
                missing.append(field_name)
                continue

            value = record[field_name]
            if value is None:
                missing.append(field_name)
                continue

            if isinstance(value, str) and value.strip() == "":
                missing.append(field_name)

        if not missing:
            return []

        return [
            ValidationMessage(
                code="missing_minimum_fields",
                level="critical",
                field=None,
                message="Faltan campos mínimos operativos del registro",
                expected=self.required_minimum_fields,
                received=missing,
            )
        ]

    def _validate_types(
        self,
        record: Dict[str, Any],
    ) -> Tuple[List[ValidationMessage], List[ValidationMessage]]:
        errors: List[ValidationMessage] = []
        warnings: List[ValidationMessage] = []

        for field_name, value in record.items():
            if field_name not in self.fields:
                continue

            meta = self.fields[field_name]
            expected_type = meta["type"]
            nullable = meta.get("nullable", True)

            if value is None:
                if not nullable:
                    errors.append(
                        ValidationMessage(
                            code="non_nullable_null",
                            level="critical",
                            field=field_name,
                            message="Campo no nullable recibido como NULL",
                            expected=expected_type,
                            received=None,
                        )
                    )
                continue

            if not self._matches_type(expected_type, value):
                errors.append(
                    ValidationMessage(
                        code="invalid_type",
                        level="error",
                        field=field_name,
                        message="Tipo inválido para el campo",
                        expected=expected_type,
                        received=type(value).__name__,
                    )
                )
                continue

            if expected_type == "date" and isinstance(value, str) and not self._is_valid_date(value):
                errors.append(
                    ValidationMessage(
                        code="invalid_date",
                        level="error",
                        field=field_name,
                        message="Fecha mal formateada",
                        expected="YYYY-MM-DD",
                        received=value,
                    )
                )

            if expected_type == "datetime" and isinstance(value, str) and not self._is_valid_datetime(value):
                errors.append(
                    ValidationMessage(
                        code="invalid_datetime",
                        level="error",
                        field=field_name,
                        message="Datetime mal formateado",
                        expected="ISO-8601",
                        received=value,
                    )
                )

        return errors, warnings

    def _validate_null_density(
        self,
        record: Dict[str, Any],
    ) -> Tuple[List[ValidationMessage], bool, bool, float]:
        total_contract_fields = len(self.fields)
        null_count = 0

        for field_name in self.fields:
            value = record.get(field_name, None)
            if value is None:
                null_count += 1
                continue
            if isinstance(value, str) and value.strip() == "":
                null_count += 1

        null_percentage = null_count / total_contract_fields if total_contract_fields else 0.0
        messages: List[ValidationMessage] = []
        warning_flag = False
        critical_flag = False

        if null_percentage >= self.null_critical_threshold:
            critical_flag = True
            messages.append(
                ValidationMessage(
                    code="critical_null_density",
                    level="error",
                    field=None,
                    message="El registro presenta una densidad crítica de NULL",
                    expected=f"< {self.null_critical_threshold:.0%}",
                    received=f"{null_percentage:.0%}",
                )
            )
        elif null_percentage >= self.null_warning_threshold:
            warning_flag = True
            messages.append(
                ValidationMessage(
                    code="high_null_density",
                    level="warning",
                    field=None,
                    message="El registro presenta alta densidad de NULL",
                    expected=f"< {self.null_warning_threshold:.0%}",
                    received=f"{null_percentage:.0%}",
                )
            )

        return messages, warning_flag, critical_flag, null_percentage

    def _validate_technical_minimum(self, record: Dict[str, Any]) -> Tuple[List[ValidationMessage], bool]:
        non_null_technical = self._count_non_null_technical_fields(record)
        if non_null_technical >= self.minimum_technical_non_null:
            return [], False

        return [
            ValidationMessage(
                code="low_technical_content",
                level="warning",
                field=None,
                message="Contenido técnico mínimo insuficiente para el registro",
                expected=f">= {self.minimum_technical_non_null} campos técnicos no nulos",
                received=non_null_technical,
            )
        ], True

    def _matches_type(self, expected_type: str, value: Any) -> bool:
        if expected_type == "string":
            return isinstance(value, str)
        if expected_type == "integer":
            return isinstance(value, int) and not isinstance(value, bool)
        if expected_type == "number":
            return (isinstance(value, int) and not isinstance(value, bool)) or isinstance(value, float)
        if expected_type == "boolean":
            return isinstance(value, bool)
        if expected_type in {"date", "datetime"}:
            return isinstance(value, str)
        return False

    @staticmethod
    def _is_valid_date(value: str) -> bool:
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    @staticmethod
    def _is_valid_datetime(value: str) -> bool:
        try:
            normalized = value.replace("Z", "+00:00")
            datetime.fromisoformat(normalized)
            return True
        except ValueError:
            return False

    def _count_non_null_technical_fields(self, record: Dict[str, Any]) -> int:
        count = 0
        for field_name in self.minimum_technical_fields:
            value = record.get(field_name)
            if value is None:
                continue
            if isinstance(value, str) and value.strip() == "":
                continue
            count += 1
        return count

    @staticmethod
    def _to_log(message: ValidationMessage) -> Dict[str, Any]:
        return {
            "code": message.code,
            "level": message.level,
            "field": message.field,
            "message": message.message,
            "expected": message.expected,
            "received": message.received,
        }


def _demo_record_ok() -> Dict[str, Any]:
    """Registro mínimo válido para ejecución local de ejemplo."""
    return {
        "version_id": "seat_ibiza_2021_1.0_tsi_95_style",
        "manufacturer_id": "seat",
        "model_id": "ibiza",
        "generation_id": "ibiza_kj_2021",
        "source": "encycarpedia",
        "source_version_url": "https://example.com/seat-ibiza-version",
        "manufacturer_name": "SEAT",
        "model_name": "Ibiza",
        "generation_name": "KJ 2021",
        "version_name": "1.0 TSI 95 Style",
        "power_cv": 95,
        "fuel_type": "petrol",
        "gearbox_type": "manual",
        "engine_displacement_cc": 999,
        "scrape_date": "2026-03-28",
        "scrape_timestamp": "2026-03-28T10:15:00Z",
    }


def _demo_record_bad() -> Dict[str, Any]:
    """Registro con incidencias estructurales para ejemplo local."""
    return {
        "version_id": "seat_ibiza_x",
        "manufacturer_id": "seat",
        "model_id": "ibiza",
        "generation_id": None,
        "source": "encycarpedia",
        "source_version_url": "",
        "manufacturer_name": "SEAT",
        "model_name": "Ibiza",
        "generation_name": "KJ",
        "version_name": 123,
        "power_cv": "95",
        "scrape_date": "28/03/2026",
        "scrape_timestamp": "ayer",
        "campo_inventado": "ruido",
    }


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parents[3]
    contract_path = repo_root / "contracts" / "catalogo" / "t_versiones.contract.json"

    print("[IIG_Catalogo] Ejecución local de ejemplo")
    print(f"Contrato esperado: {contract_path}")

    iig = IIG_Catalogo(contract_path=contract_path, mode="observacion")

    ok_result = iig.validate_record(_demo_record_ok())
    bad_result = iig.validate_record(_demo_record_bad())
    batch_result = iig.validate_batch([_demo_record_ok(), _demo_record_bad()])

    print("\n--- REGISTRO OK ---")
    print(json.dumps(asdict(ok_result), ensure_ascii=False, indent=2, default=str))

    print("\n--- REGISTRO CON INCIDENCIAS ---")
    print(json.dumps(asdict(bad_result), ensure_ascii=False, indent=2, default=str))

    print("\n--- LOTE ---")
    print(json.dumps(asdict(batch_result), ensure_ascii=False, indent=2, default=str))
