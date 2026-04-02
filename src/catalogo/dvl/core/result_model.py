from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ValidationResult:
    """Resultado estándar del DVL_Catalogo.

    El DVL no infiere ni corrige datos. Solo:
    - normaliza superficialmente
    - detecta errores críticos
    - detecta warnings no bloqueantes
    - calcula métricas de calidad
    """

    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    normalized_data: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
