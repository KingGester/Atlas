from dataclasses import dataclass

from .execution_context import ExecutionContext
from .identity import IdentityContext
from .observability_context import ObservabilityContext
from .policy_context import PolicyContext
from .request_info import RequestInfo
from .response_context import ResponseContext
from .routing_context import RoutingContext


@dataclass(slots=True)
class RequestContext:
    identity: IdentityContext
    request: RequestInfo
    policy: PolicyContext
    routing: RoutingContext
    execution: ExecutionContext
    response: ResponseContext
    observability: ObservabilityContext