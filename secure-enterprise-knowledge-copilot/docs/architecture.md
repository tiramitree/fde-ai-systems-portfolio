# Architecture

## Current MVP

```text
Static ES-module UI
  +-- api.js: HTTP client
  +-- dom.js: safe DOM helpers
  +-- renderers.js: UI rendering
  +-- app.js: screen orchestration
  |
  | HTTP JSON
  v
Python standard-library HTTP server
  |
  +-- api.py: application API layer
  |
  +-- repositories.py: application-facing storage adapter boundary
  |
  +-- Ingestion
  |   +-- admin-only document intake
  |   +-- source text normalization
  |   +-- classification and role validation
  |   +-- source hashing and audit event
  |
  +-- JSON runtime storage adapter
  |   +-- users
  |   +-- documents
  |   +-- chunks
  |   +-- traces
  |   +-- audit_events
  |   +-- eval_runs
  |
  +-- Retrieval
  |   +-- tenant filter
  |   +-- role filter
  |   +-- BM25-like keyword score
  |   +-- synonym expansion
  |
  +-- Answering
  |   +-- retrieved evidence sanitization
  |   +-- citation selection
  |   +-- abstention threshold
  |
  +-- Security
  |   +-- prompt injection pattern detection
  |   +-- unsafe retrieved lines ignored
  |
  +-- Evals
      +-- expected answer/abstain behavior
      +-- required and forbidden citations
      +-- unsafe leak checks
```

## Production Upgrade

```text
Next.js UI
  -> API gateway
  -> FastAPI services
  -> PostgreSQL + pgvector
  -> Redis queue
  -> object storage
  -> OpenAI Responses API
  -> OpenTelemetry / trace backend
  -> eval runner in CI
```

## Key Design Decisions

Permission filtering happens before evidence is assembled. The model should never receive chunks the user cannot access.

Ingestion is an application boundary, not a frontend shortcut. Only admin users can add searchable documents, and each new document records source hash, chunk count, source MIME type, roles, and classification in the audit log.

The application modules depend on `KnowledgeRepository` rather than direct JSON state. The current `JsonKnowledgeRepository` keeps the local demo zero-dependency, while the PostgreSQL/pgvector migration path can attach behind the same interface.

Retrieved documents are treated as data, not instructions. Instruction-like text inside documents is detected and excluded from evidence.

The answer shape is structured around answer, citations, confidence, missing evidence, abstain reason, and security events. This makes the output inspectable and testable.

The static UI is separated from the application API. The HTTP server only parses requests and serves assets; the API layer owns endpoint behavior; frontend modules own API calls, DOM helpers, rendering, and screen orchestration separately.

Eval cases include required citations and forbidden citations. This catches both quality regressions and permission leaks.
