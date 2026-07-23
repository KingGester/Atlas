from dataclasses import dataclass, field


@dataclass(slots=True)
class PolicyContext:
    constraints: list[str] = field(default_factory=list)
    objective: str = "balanced"