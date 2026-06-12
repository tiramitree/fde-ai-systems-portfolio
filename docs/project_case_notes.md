# Project Case Notes

## System Positioning

This repository contains three local-first enterprise AI reference systems:

- a secure knowledge copilot for permission-aware retrieval
- a governed operations agent for tool use and approval control
- a reliability console for AI release incidents and eval regressions

The systems are designed as inspectable implementation references for teams that need model-facing applications with deterministic safety boundaries, auditability, and regression gates.

## Project 1 Impact

The knowledge copilot demonstrates role-based retrieval, citation enforcement, abstention, retrieved-content prompt-injection handling, trace logging, audit events, and eval-gated regression tests. It keeps authorization and evidence assembly outside the model so unauthorized evidence is never sent into generation.

## Project 2 Impact

The operations agent demonstrates governed tool calling for product-recall workflows. It can investigate cases, cite policies, create internal records, draft seller notices, and schedule follow-up, while external side effects remain blocked behind tool-registry policy, dry-run preview, supervisor approval, rejection/expiry terminal states, sanitized action-outbox dispatch, idempotent execution, and an action-run receipt with payload hash and output references.

## Project 3 Impact

The reliability console demonstrates AI release operations after deployment. It links canary incidents to failed eval cases, produces deterministic rollout decisions, blocks unsafe release expansion, and records remediation, trace, and audit evidence.

## Review Flow

1. Open Project 1 and show role-aware access with Alice and Morgan.
2. Show Project 1 abstention and prompt-injection handling.
3. Run Project 1 evals.
4. Open Project 2 and run the Market Blue investigation.
5. Show approval queue behavior and blocked direct `send_notice`.
6. Approve as supervisor and inspect audit evidence.
7. Open Project 3 and triage the high-risk canary incident.
8. Show failed eval evidence, blocked rollout, remediation guidance, trace records, and audit events.
9. Run all project evals and the repository smoke gate.

## Core Technical Claims

- Permission checks happen before evidence assembly.
- Retrieved content is treated as data, not instructions.
- Side-effect tools are gated by application logic, not model promises.
- Release decisions are blocked by deterministic eval and incident evidence.
- Evals include negative cases and bypass attempts.
- Traces and audit logs are first-class product surfaces.

## Production Upgrade Path

The current local version is dependency-free for reliable review and release validation. Production adapters would replace local stores with PostgreSQL and pgvector, move APIs to FastAPI or another service framework, add authenticated connectors, integrate OpenAI Responses API or Agents SDK behind structured schemas, export OpenTelemetry traces, and run eval gates in CI/CD.
