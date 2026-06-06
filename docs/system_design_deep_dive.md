# System Design Deep Dive

## Problem Statement

Design a reference-quality enterprise AI system that demonstrates:

- secure knowledge access
- governed tool execution
- eval-driven iteration
- traceable and auditable behavior
- clear production upgrade path

## Core Design Principle

The model is a reasoning component, not the security boundary.

Security and governance are enforced through application logic:

- ACL filtering
- approval middleware
- idempotency keys
- audit log writes
- eval gates

## Shared Platform Pattern

```text
Frontend
  -> API handler
  -> user/session context
  -> policy gate
  -> retrieval/tool layer
  -> model gateway
  -> structured output parser
  -> trace logger
  -> audit logger
  -> eval runner
```

## Project 1 Request Flow

```text
question
  -> resolve user role and source groups
  -> retrieve tenant chunks
  -> filter by tenant, role, source group, and source principals
  -> detect unsafe retrieved instructions
  -> select evidence
  -> answer or abstain
  -> attach chunk and sentence evidence citations
  -> write trace
  -> write audit
```

Failure modes:

- retrieval miss
- stale document
- wrong ACL metadata
- prompt injection
- overconfident answer
- bad citation

Controls:

- permission filter before answer generation
- citation requirement with parser-normalized chunk and answer-support spans
- abstention threshold
- prompt-injection detection
- eval cases for leaks and unsupported questions

## Project 2 Request Flow

```text
message
  -> classify intent
  -> detect bypass prompt
  -> search policy
  -> search listings
  -> create internal violation
  -> draft notice
  -> schedule follow-up
  -> create approval request
  -> supervisor approval
  -> side-effect execution
  -> audit and trace
```

Failure modes:

- wrong intent
- wrong listing
- skipped approval
- duplicate notice
- bad policy citation
- hidden unsafe instruction

Controls:

- side-effect tool block
- supervisor-only approval endpoint
- idempotency key
- audit log
- unsafe-action evals

## Production Data Model

Project 1:

- users
- roles
- tenants
- documents
- document ACLs
- chunks
- embeddings
- retrieval traces
- answer traces
- audit events
- eval runs

Project 2:

- users
- cases
- sellers
- products
- listings
- policies
- violations
- approvals
- notices
- followups
- tool calls
- audit events
- eval runs

## Production Stack

Recommended:

- Next.js frontend
- FastAPI backend
- PostgreSQL
- pgvector
- Redis queue
- OpenAI Responses API
- OpenAI Agents SDK for agent workflow if needed
- OpenTelemetry
- GitHub Actions eval gate
- Docker Compose for local production-like environment

## Scalability Considerations

Project 1:

- async ingestion
- batch embeddings
- chunk versioning
- document ACL invalidation
- hybrid search indexes
- cache high-frequency policy answers

Project 2:

- workflow state machine
- connector-specific retry policy
- idempotent external side effects
- approval SLA tracking
- dead-letter queue for failed tools

## Security Considerations

- row-level security
- audit log immutability
- PII redaction
- per-tool authorization
- connector-scoped credentials
- prompt-injection red-team suite
- data retention policies

## What Makes This Technical Review-Strong

The projects are not impressive because of model novelty. They are strong because they show production judgment:

- where to trust the model
- where not to trust the model
- how to evaluate behavior
- how to debug failures
- how to explain tradeoffs
- how to upgrade without changing safety boundaries
