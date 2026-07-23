from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class IdentityContext:
    request_id: str
    trace_id: str
    created_at: datetime