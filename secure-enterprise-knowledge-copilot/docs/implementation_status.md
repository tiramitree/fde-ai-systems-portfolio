# Implementation Status

Date: 2026-06-06

## Current Runnable State

The Project 1 MVP is runnable locally.

Project path:

```text
secure-enterprise-knowledge-copilot
```

Run command:

```powershell
cd secure-enterprise-knowledge-copilot
python -B app.py --reset --port 8765
```

Local URL:

```text
http://127.0.0.1:8765
```

Eval command:

```powershell
python -B scripts\run_eval.py
```

## Verified Capabilities

- Static UI loads in browser.
- API health endpoint returns OK.
- Role-aware document visibility works.
- Alice can answer general internal-policy questions with citations.
- Alice cannot answer confidential finance-plan questions.
- Morgan can answer finance-plan questions with a finance citation.
- Retrieved prompt-injection content is detected and excluded from answer evidence.
- Unknown questions abstain instead of fabricating.
- Audit events are recorded.
- Trace records include retrieved chunks, blocked count, output, confidence, and security events.
- Admin ingestion normalizes plain text, Markdown, CSV, HTML, and JSON through a parser boundary before span-aware chunking.
- Citations and retrieved chunks expose normalized-text source spans for review and traceability.
- Retrieval uses an `active_sources_only` source lifecycle policy so superseded sources remain in the store for audit history but are filtered before scoring and answer assembly.
- Evals include a stale-source regression case that must cite the current policy and filter the superseded policy.
- Seed and admin-ingested chunks carry deterministic local embeddings with model `local-hashing-v1` and 1536 dimensions.
- Retrieval exposes candidate strategy metadata: the default JSON path uses `local_full_scan`, while the optional PostgreSQL path uses SQL-backed `postgres_hybrid_sql_v1`.
- Retrieval exposes deterministic rerank metadata with `local-evidence-reranker-v1`, `rerank_score`, and feature-level `rerank_breakdown`.
- UI eval button runs the golden eval suite.
- CLI eval suite passes.

Latest CLI eval result:

```text
total_cases: 14
passed_cases: 14
pass_rate: 1.0
unsafe_leak_failures: 0
```

## Current Technical Scope

The MVP uses:

- Python standard-library HTTP server
- JSON runtime state
- Static HTML/CSS/JS frontend
- BM25-like keyword retrieval with synonym expansion
- Local hybrid retrieval profile with lexical, title, phrase, semantic-family, and vector score breakdowns
- Source lifecycle filtering with `source_lifecycle_state`, `superseded_by`, and `stale_filtered_count`
- Deterministic evidence reranker boundary with inspectable rerank features
- Local deterministic embedding boundary for chunk metadata and pgvector handoff
- Optional PostgreSQL/pgvector adapter contract with SQL keyword/vector candidate selection
- Tenant and role filtering before evidence assembly
- Deterministic extractive answer assembly
- Citation-required answer shape
- Abstention threshold
- Prompt-injection pattern detection
- Admin source parser boundary for text, Markdown, CSV, HTML, and JSON
- Trace and audit logging
- Golden eval cases

This is intentionally dependency-free because the current local Node execution was blocked and SQLite file operations were unreliable in the environment.

## Not Yet Production-Grade

Still missing before calling the full FDE objective complete:

- FastAPI backend
- Next.js or production frontend
- Live PostgreSQL/pgvector deployment validation beyond the optional adapter, migration, seed, and compose artifacts
- Production embedding model and reranker provider
- Production SQL retrieval metrics and broader reranker comparison
- File upload, PDF/DOCX/OCR support, and connector-backed document parser pipeline
- Background ingestion worker
- OpenAI Responses API structured output
- OpenTelemetry or external trace backend
- Cloud deployment or managed Docker deployment
- Auth provider integration
- PII redaction pipeline
- Screenshot/demo video package
- Full deployment runbook
- Project 2 Regulated Customer Operations Agent

## Next Engineering Step

Convert the current MVP into an industrialized service layout without losing the runnable demo:

1. Run the live PostgreSQL probe against a seeded Docker-enabled machine and record the evidence.
2. Extend the current admin parser boundary into upload, connector sync, and background ingestion.
3. Replace the deterministic embedding boundary with a production provider behind the same interface.
4. Add retrieval metrics for SQL candidate recall, citation span accuracy, larger stale/conflict fixtures, and reranker quality.
5. Add FastAPI-compatible service layer or migrate directly to FastAPI if dependencies are available.


