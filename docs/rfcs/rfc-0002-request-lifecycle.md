# RFC-0002: Request Lifecycle

Status: Draft
Owner: CTO
Last Updated: 2026-07-16

## Summary

This RFC defines the end-to-end lifecycle of a request in Atlas v0.1.

It explains what happens from the moment a user sends `client.chat(...)` to the moment Atlas returns a standardized response.
It also defines component ownership, request context, execution boundaries, error flow, observability points, and architectural invariants.

## Motivation

Atlas is a control plane for model decisions.
Before implementation begins, Atlas must define a deterministic request lifecycle.

Without a clear lifecycle:

- component ownership becomes ambiguous
- interfaces drift during implementation
- error handling becomes inconsistent
- observability becomes fragmented
- architectural boundaries erode over time

## Goals

- define the end-to-end execution flow
- assign clear ownership to each stage
- define the request context created and used during execution
- define component boundaries
- define observability checkpoints
- define the initial error flow for v0.1
- define invariants that must remain true as Atlas evolves

## Non-Goals

This RFC does not define:

- learned routing
- speculative execution
- advanced retry orchestration
- multi-step fallback trees
- streaming lifecycle details
- automatic policy optimization
- full eval pipeline

## Lifecycle Overview

The v0.1 request lifecycle is:

1. SDK receives user request
2. SDK translates the request into Atlas request format
3. Atlas Core creates request context and trace context
4. Policy Engine validates policy inputs and returns executable constraints/objectives
5. Atlas Core resolves eligible execution targets
6. Router decides the best execution target
7. Provider Adapter executes the request against the selected provider
8. Provider Adapter normalizes the provider response or error
9. Atlas Core records trace, metrics, latency, usage, and cost
10. SDK returns the standardized response to the user

## Lifecycle Diagram

```text
User
  ->
Atlas SDK
  ->
Atlas Core
  ->
Policy Engine
  ->
Candidate Resolution
  ->
Router
  ->
Provider Adapter
  ->
Provider
  ->
Provider Adapter
  ->
Atlas Core
  ->
Atlas SDK
  ->
User
```

## Ownership Table

| Stage | Owner | Responsibility |
|---|---|---|
| Request Input | SDK | Accept user-facing API call |
| Request Translation | SDK | Translate SDK input into Atlas request format |
| Context Creation | Atlas Core | Create request context, trace context, and lifecycle state |
| Policy Evaluation | Policy Engine | Validate policy inputs and produce constraints/objectives |
| Candidate Resolution | Atlas Core | Resolve eligible execution targets before routing |
| Route Decision | Router | Decide the best target and explain the decision |
| Provider Execution | Provider Adapter | Execute request against provider |
| Response Normalization | Provider Adapter | Normalize provider response or provider error |
| Observability Finalization | Atlas Core | Record trace, metrics, usage, latency, and cost |
| Response Delivery | SDK | Return standardized response to caller |

## Single-Verb Responsibilities

Each major component should preserve one dominant architectural verb:

- `SDK` translates
- `Atlas Core` coordinates
- `Policy Engine` validates
- `Router` decides
- `Provider Adapter` executes

These verbs are architectural guardrails.
If a component starts taking on another component's dominant verb, the boundary should be re-evaluated.

## Request Context

Atlas Core creates a request context at the start of execution.

The request context is the internal execution object that carries request-scoped state across the lifecycle.

It should contain at least:

- request ID
- tenant
- virtual model
- input request payload
- policy input or policy reference
- deadline or timeout budget
- metadata
- trace context
- objectives
- constraints
- candidate set
- selected route decision
- execution status

The exact schema will be defined in `RFC-0004: Data Model`.

## Candidate Resolution

Before routing begins, Atlas Core resolves the list of eligible execution targets.

An execution target may include:

- provider
- model
- region
- adapter binding

Candidate resolution is not route decision-making.
Its job is to prepare the eligible target set that the Router will evaluate.

In v0.1, Atlas Core owns candidate resolution so that:

- Router remains focused on decision-making only
- registry concerns stay outside Router
- testability remains high
- future registry evolution does not force Router redesign

## Step-by-Step Execution Flow

### Step 1: Request Input
Owner: `SDK`

The SDK receives a user-facing request such as `client.chat(...)`.

Output:
- Atlas-compatible request payload

Failure modes:
- invalid client configuration
- missing authentication
- malformed SDK input

Observability:
- request received
- sdk version
- client metadata

### Step 2: Request Translation
Owner: `SDK`

The SDK translates the user-facing API shape into the standardized Atlas request format.

Output:
- normalized Atlas request

Failure modes:
- serialization failure
- unsupported SDK option

Observability:
- normalized request created
- translation warnings if any

### Step 3: Context Creation
Owner: `Atlas Core`

Atlas Core creates the request context and initializes trace context.

Output:
- request context
- trace context
- lifecycle state initialized

Failure modes:
- invalid normalized request
- missing required fields

Observability:
- request ID assigned
- tenant identified
- virtual model identified

### Step 4: Policy Evaluation
Owner: `Policy Engine`

The Policy Engine interprets policy inputs and returns executable constraints and objectives.

Output:
- constraints
- objectives
- policy evaluation metadata

Failure modes:
- invalid policy configuration
- unresolved policy reference
- contradictory constraints

Observability:
- policy evaluation completed
- policy version
- constraints count
- objectives count

### Step 5: Candidate Resolution
Owner: `Atlas Core`

Atlas Core resolves the list of eligible execution targets prior to routing.

Output:
- candidate set

Failure modes:
- no registered targets
- registry inconsistency
- no candidate satisfies baseline eligibility

Observability:
- candidate count
- filtered candidate count
- virtual model to candidate mapping

### Step 6: Route Decision
Owner: `Router`

The Router evaluates the candidate set against constraints and objectives and decides the best target.

Output:
- route decision
- selected target
- rejected candidates
- reason codes

Failure modes:
- no viable target
- malformed candidate metadata
- inconsistent ranking inputs

Observability:
- routing latency
- selected target
- rejected candidate reasons
- decision reason codes

### Step 7: Provider Execution
Owner: `Provider Adapter`

The Provider Adapter translates the standardized Atlas request into a provider-specific API call and executes it.

Output:
- raw provider response or raw provider error

Failure modes:
- timeout
- authentication error
- rate limit
- transport failure
- provider API error

Observability:
- provider selected
- model selected
- region selected
- execution start time
- execution end time

### Step 8: Response Normalization
Owner: `Provider Adapter`

The Provider Adapter normalizes the provider response or error into Atlas-standard format.

Output:
- standardized Atlas response or standardized Atlas error

Failure modes:
- response parsing error
- incomplete provider metadata
- non-normalizable upstream error

Observability:
- normalization completed
- token usage extracted
- provider metadata captured

### Step 9: Observability Finalization
Owner: `Atlas Core`

Atlas Core finalizes trace, metrics, cost, and lifecycle outcome data.

Output:
- completed trace
- metrics record
- usage record
- cost record

Failure modes:
- telemetry write failure
- partial cost metadata
- non-blocking trace persistence failure

Observability:
- total latency
- route decision
- token usage
- estimated cost
- final status

### Step 10: Response Delivery
Owner: `SDK`

The SDK returns the standardized response to the caller.

Output:
- final user-facing response

Failure modes:
- sdk deserialization mismatch
- response transport issue

Observability:
- response returned
- end-to-end success/failure

## Error Flow

In v0.1, provider execution errors flow through the following path:

```text
Provider
  ->
Provider Adapter
  ->
Atlas Core
  ->
Atlas SDK
  ->
User
```

Error ownership is defined as follows:

- `Provider Adapter` normalizes upstream provider errors
- `Atlas Core` classifies the lifecycle outcome and records observability data
- `Atlas SDK` returns the standardized error to the caller

Initial error categories include:

- request validation error
- policy evaluation error
- candidate resolution error
- no viable route error
- provider timeout error
- provider authentication error
- provider rate limit error
- provider transport error
- provider response normalization error

In v0.1, advanced retry and fallback behavior are explicitly out of scope unless defined by a later RFC.

## Observability

At minimum, Atlas should record the following per request:

- request ID
- tenant
- virtual model
- policy version
- candidate count
- selected provider
- selected model
- selected region if present
- route decision reason codes
- request latency
- provider latency
- token usage
- estimated cost
- final status
- normalized error type if failed

Core lifecycle events should include:

- request received
- request normalized
- context created
- policy evaluated
- candidates resolved
- route decided
- provider execution started
- provider execution completed
- response normalized
- request completed
- request failed

## Future Extensions

The following may be added in later RFCs, but are not part of this RFC:

- retry orchestration
- fallback execution
- streaming lifecycle
- budget enforcement flow
- provider health awareness
- speculative execution
- async evaluation hooks

## Invariants

The following rules must always remain true:

- Router never executes requests.
- Policy Engine never selects providers directly.
- Provider Adapter never modifies routing decisions.
- Atlas Core is the only orchestration entry point.
- Candidate resolution happens before route decision.
- Route decision happens before provider execution.
- Atlas response format is provider-neutral from the caller's perspective.

## Open Questions

- Should request validation happen in both SDK and Core, or should Core remain the only authority?
- Should `RouteDecision` always include rejected candidates, or only selected target plus reason codes?
- Should trace persistence be synchronous or partially asynchronous in v0.1?
- Should cost in v0.1 be estimated only, or exact when provider metadata is available?
- Should deadline enforcement belong to Core, Adapter, or both?

## Decision

Pending review.