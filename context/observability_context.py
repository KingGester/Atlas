from dataclasses import dataclass, field


@dataclass(slots=True)
class ObservabilityContext:
    events: list[str] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)