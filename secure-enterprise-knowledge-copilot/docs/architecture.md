# Architecture

## Current MVP

```text
Static HTML/JS UI
  |
  | HTTP JSON
  v
Python standard-library HTTP server
  |
  +-- JSON runtime storage
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

Retrieved documents are treated as data, not instructions. Instruction-like text inside documents is detected and excluded from evidence.

The answer shape is structured around answer, citations, confidence, missing evidence, abstain reason, and security events. This makes the output inspectable and testable.

Eval cases include required citations and forbidden citations. This catches both quality regressions and permission leaks.
