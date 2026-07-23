from dataclasses import dataclass


@dataclass(slots=True)
class RoutingContext:
    provider: str | None = None
    model: str | None = None
    reason: str | None = None