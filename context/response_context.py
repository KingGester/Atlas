from dataclasses import dataclass


@dataclass(slots=True)
class ResponseContext:
    latency_ms: float | None = None
    status: str = "pending"