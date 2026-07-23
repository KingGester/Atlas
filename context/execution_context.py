from dataclasses import dataclass
from time import monotonic


@dataclass(slots=True)
class ExecutionContext:
    started_at: float = monotonic()
    deadline_ms: int | None = None
    retry_count: int = 0