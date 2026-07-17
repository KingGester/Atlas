# RFC-0004: Core Data Model

Status: Draft

Authors: Atlas Team

Owner: CTO

Created: 2026-07-17

Last Updated: 2026-07-17

Target Release: v0.1

Related RFCs:
- RFC-0001 Product Vision
- RFC-0002 Request Lifecycle
- RFC-0003 Core Interfaces

---

# Summary

This RFC defines the canonical data model used by Atlas.

Every component inside Atlas communicates using these models.

The data model is provider-independent and language-independent.

No component may exchange provider-specific objects directly.

---

# Motivation

Atlas is a control plane.

A control plane only works if every component speaks the same language.

Without a canonical data model:

- providers leak into business logic
- components become tightly coupled
- adapters become inconsistent
- testing becomes difficult

---

# Design Principles

- Provider agnostic
- Immutable whenever possible
- Explicit ownership
- Strong typing
- Minimal but extensible
- Stable across providers

---

# Core Objects

Atlas v0.1 defines the following core objects.

- RequestContext
- ChatRequest
- Candidate
- Constraint
- Objective
- RouteDecision
- ProviderRequest
- ProviderResponse
- ChatResponse
- Trace

---

# RequestContext

Represents the execution context of one request.

Owner:

Atlas Core

Contains:

- request_id
- timestamp
- tenant
- user
- objective
- constraints
- metadata
- trace_id
- deadline
- execution_state

Lifecycle:

Created once.

Lives during the entire execution.

Destroyed after completion.

---

# ChatRequest

Represents a normalized user request.

Owner:

SDK

Contains:

- virtual_model
- messages
- tools
- attachments
- response_format
- temperature
- max_tokens
- metadata

Provider-independent.

---

# Candidate

Represents one possible execution target.

Examples:

- GPT-5
- Claude Sonnet
- Gemini Pro
- Local Llama

Contains:

- provider
- model
- region
- capabilities
- estimated_cost
- estimated_latency
- health_status

Created by:

Atlas Core

Consumed by:

Router

---

# Constraint

Represents execution restrictions.

Examples:

- EU only
- Vision required
- Tool calling required
- Max cost
- Max latency
- Approved provider

Produced by:

Policy Engine

Consumed by:

Router

---

# Objective

Represents optimization goals.

Examples:

- Lowest Cost
- Highest Quality
- Lowest Latency
- Balanced
- Enterprise Policy

Only one objective is active for each request.

---

# RouteDecision

Represents the final routing decision.

Owner:

Router

Contains:

- selected_provider
- selected_model
- selected_region
- routing_reason
- rejected_candidates

Immutable.

---

# ProviderRequest

Internal request sent to a provider.

Owner:

Provider Adapter

Contains:

- endpoint
- authentication
- payload
- timeout
- provider_options

Never exposed outside Provider Adapter.

---

# ProviderResponse

Normalized provider result.

Contains:

- output
- usage
- finish_reason
- latency
- provider_metadata

Provider-specific fields are normalized before leaving the adapter.

---

# ChatResponse

Final response returned to the SDK.

Contains:

- content
- model
- provider
- usage
- cost_estimate
- trace_id

Must remain provider-independent.

---

# Trace

Represents execution telemetry.

Owner:

Atlas Core

Contains:

- request_id
- route_decision
- provider
- latency
- cost
- policy_version
- execution_steps
- errors

Every request produces exactly one trace.

---

# Object Relationships

```
ChatRequest
      │
      ▼
RequestContext
      │
      ▼
Policy Engine
      │
      ▼
Constraints
      │
      ▼
Candidates
      │
      ▼
Router
      │
      ▼
RouteDecision
      │
      ▼
ProviderRequest
      │
      ▼
Provider Adapter
      │
      ▼
ProviderResponse
      │
      ▼
ChatResponse
      │
      ▼
Trace
```

---

# Ownership

| Object | Owner |
|---------|-------|
| ChatRequest | SDK |
| RequestContext | Atlas Core |
| Candidate | Atlas Core |
| Constraint | Policy Engine |
| Objective | Policy Engine |
| RouteDecision | Router |
| ProviderRequest | Provider Adapter |
| ProviderResponse | Provider Adapter |
| ChatResponse | SDK |
| Trace | Atlas Core |

---

# Invariants

The following rules must never be violated.

- RequestContext exists exactly once.
- RouteDecision is immutable.
- ProviderResponse never leaves Adapter unnormalized.
- ChatResponse never contains provider-specific structures.
- Every request generates one Trace.
- Every execution has one Objective.
- Every Candidate must contain capability metadata.

---

# Future Extensions

Future RFCs may introduce:

- StreamingChunk
- BudgetReport
- EvaluationResult
- MemoryReference
- AgentExecution
- ToolExecution
- Event
- Checkpoint

These are intentionally excluded from v0.1.

---

# Compatibility

Core objects are considered stable.

New optional fields may be added.

Existing fields must not change semantics.

Breaking changes require a new RFC.