from dataclasses import dataclass, field
from typing import Dict


@dataclass
class PipelineResult:
    processed: int = 0
    inserted: int = 0
    skipped_duplicates: int = 0
    pending_recoverable: int = 0
    rejected_technical: int = 0
    failed: int = 0

    causes: Dict[str, int] = field(default_factory=dict)