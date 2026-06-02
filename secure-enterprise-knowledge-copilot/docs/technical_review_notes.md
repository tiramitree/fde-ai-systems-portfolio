# Technical Review Notes

## System Summary

The secure knowledge copilot answers internal policy questions only from documents the user is allowed to access. It requires citations, abstains when evidence is insufficient, records traces and audit events, and runs a golden eval set to prevent regressions.

## Why It Matters

Enterprise RAG needs permissions, data-leak prevention, auditability, answer quality checks, deployment gates, and debugging surfaces. This project demonstrates those concerns end to end with a deterministic local implementation.

## Main Tradeoffs

SQLite and a local answerer make the MVP runnable without dependencies. The production path is PostgreSQL/pgvector, FastAPI, queue-based ingestion, and OpenAI Responses API structured outputs.

The MVP uses deterministic extraction instead of generation so security and eval behavior is reproducible locally. In production, a model gateway can generate final answers from sanitized accessible evidence with a strict structured schema.

The permission filter is applied before answer generation. This reduces leakage risk compared with retrieving everything and asking the model to ignore forbidden chunks.

## Failure Modes

- Wrong or stale document metadata can cause bad permissions.
- Poor chunking can reduce citation quality.
- Keyword retrieval can miss semantic matches.
- Prompt-injection patterns can be more subtle than simple pattern checks.
- Eval sets can become too narrow unless refreshed from real failures.

## Next Improvements

- Add file upload and background ingestion.
- Add dense embeddings and reranking.
- Add Responses API structured output.
- Add OpenTelemetry trace export.
- Add Docker Compose with PostgreSQL and worker service.
- Add real auth provider integration.
