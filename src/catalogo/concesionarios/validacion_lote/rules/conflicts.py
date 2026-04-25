from typing import List

from ...models.concesionario_resolved import ConcesionarioResolved


def detect_conflicts(records: List[ConcesionarioResolved]) -> List[str]:
    conflicts: List[str] = []

    grouped = {}
    for record in records:
        key = record.semantic_key_concesionario
        if not key:
            continue
        grouped.setdefault(key, []).append(record)

    for key, group in grouped.items():
        if len(group) < 2:
            continue

        tipos = {
            (item.validated.normalized.tipo_concesionario_normalizado or "").strip().lower()
            for item in group
        }
        localidades = {item.localidad_id for item in group}
        direcciones = {
            (item.validated.normalized.direccion_texto_normalizada or "").strip().lower()
            for item in group
        }

        tipos_limpios = {t for t in tipos if t}
        direcciones_limpias = {d for d in direcciones if d}

        if len(localidades) > 1:
            conflicts.append(
                f"conflict semantic_key={key}: misma key con multiples localidad_id={sorted(localidades)}"
            )

        if len(tipos_limpios) > 1:
            conflicts.append(
                f"conflict semantic_key={key}: tipos incompatibles={sorted(tipos_limpios)}"
            )

        if len(direcciones_limpias) > 1:
            conflicts.append(
                f"conflict semantic_key={key}: multiples direcciones normalizadas"
            )

    return conflicts