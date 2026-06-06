# Industrial Readiness Gap Plan: Source Sync Slice

Date: 2026-06-06

## Short Judgment

This repository is strong as a production-minded FDE portfolio and reference implementation. It is not yet a real enterprise production system.

Current distance estimate:

| Target | Current distance | Judgment |
| --- | --- | --- |
| Technical review / portfolio demonstration | Close | The repository has credible control boundaries, evals, traces, audit logs, UI contracts, visual checks, public repo hygiene, and CI-style quality gates. |
| Controlled internal demo | Medium | It can demonstrate the right invariants locally, but still depends on fictional seed data and local reset state. |
| Limited pilot | Far | It needs real auth, live persistence, real source connectors, parser workers, external observability, operational runbooks, and load/error testing. |
| True enterprise production | Very far | It needs identity federation, tenant isolation, source ACL sync, durable ingestion, online eval operations, incident response, backups, SLOs, and support processes. |

My updated rough score:

| Dimension | Maturity |
| --- | --- |
| Portfolio expression | 85-90% |
| Architecture credibility | 70-78% |
| Controlled local demo | 62-70% |
| Limited pilot | 35-45% |
| True production | 18-28% |

The new `/api/sources/sync` work improves the data-plane story, but it is still a connector contract and sample sync path, not a real external connector.

## External Baseline Scan

I compared the repository against common capabilities from current production-oriented AI/RAG/agent systems and docs:

| Source | What production systems emphasize | Gap for this repo |
| --- | --- | --- |
| OpenAI evaluation best practices | Eval-driven development, production/historical data, continuous evaluation, hard-coded domain cases, and context recall/precision metrics for Q&A over docs. | Current golden evals are good, but need larger realistic datasets, online trace mining, human review, continuous eval scheduling, and retrieval metrics. |
| OpenAI production best practices | Secure access, organization controls, and robust architecture for high traffic. | Current repo is local-first and has no real auth, rate limits, usage controls, or deployed high-traffic architecture. |
| Arize Phoenix | Tracing, evaluation, prompt iteration, datasets, experiments, OpenTelemetry/OpenInference integration, and self-hosting. | Current traces are local and exportable, but not sent to a live backend with dashboards, annotations, or experiment comparison. |
| Haystack evaluation | Component-level and end-to-end evaluation for retrievers, readers, generators, and RAG metrics. | Current evals validate behavior, but retrieval evaluation needs recall@k, precision, faithfulness, stale-source, conflict, and parser-quality checks. |
| LangChain/LangGraph production guidance | Thread IDs, per-run context, user auth, multi-tenancy, RBAC, async tools, durability, checkpointing, memory scoping, guardrails, and sandboxing. | Project 2 has approval concepts, but lacks durable workflow state, real user identity, async external tools, checkpoint recovery, and credential isolation. |
| Microsoft AutoGen tracing | Agent systems need OpenTelemetry-compatible tracing for debugging, performance analysis, and flow understanding. | Current OTLP-like export is a good start; production needs SDK spans around API, retrieval, model, tool, approval, and eval events. |
| Qdrant / vector DB guidance | Filtering must happen in the search layer, and payload indexes should be created for fields used in filters. | Project 1 has permission filtering and optional pgvector design, but needs live index/filter tests, source ACL indexes, and query performance checks. |
| Weaviate search docs | Production RAG commonly combines vector search, keyword/BM25, hybrid search, RAG, reranking, filters, aggregation, and query profiling. | Current local hybrid/reranker boundary is good; it still needs a real search backend and production retrieval tuning. |

Source links:

- https://developers.openai.com/api/docs/guides/evaluation-best-practices
- https://developers.openai.com/api/docs/guides/production-best-practices
- https://arize.com/docs/phoenix
- https://docs.haystack.deepset.ai/docs/evaluation
- https://docs.langchain.com/oss/python/deepagents/going-to-production
- https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tracing.html
- https://qdrant.tech/documentation/search/search/
- https://docs.weaviate.io/weaviate/search

## What We Just Added

Project 1 now has a connector-style source sync slice:

- `POST /api/sources/sync`
- admin-only source sync refusal for non-admin users
- connector metadata: `connector`, `cursor`, `acl_source`
- document metadata: `source_connector`, `external_id`, `acl_source`, `sync_cursor`
- reuse of parser, chunking, embedding, body-hiding, permission, retrieval, and citation paths
- per-document `document_ingested` audit events
- batch `source_sync_completed` audit event
- frontend `Sync connector` sample button
- runtime API contract checks proving source sync, retrieval citation, and audit evidence
- updated docs, threat model, evidence matrix, public README, screenshot manifest, and visual assets

Verification snapshot:

```text
python -B scripts/dev.py contracts
API contract checks: 68/68 passed

python -B scripts/dev.py ui-contracts
Runtime UI contract checks: 335/335 passed

python -B scripts/dev.py quality
Quality gate passed.
```

## Remaining Industrial Gaps

| Gap | Why it matters | Next proof to build |
| --- | --- | --- |
| Real authentication | UI-selected users are not an enterprise identity boundary. | Add auth middleware, tenant context, and signed local demo tokens or an OIDC-ready adapter. |
| Source ACL sync | Enterprise RAG depends on source-system permissions, not manually assigned roles. | Add a read-only connector fixture that syncs users/groups/document ACLs and proves permission drift behavior. |
| Durable ingestion | Real ingestion has retries, failures, large files, deletion, and backfills. | Add ingestion jobs, cursor checkpoints, job status, dead-letter records, and retry/idempotency checks. |
| Document parsing depth | Real corpora include PDF/DOCX/tables/OCR and malformed content. | Add parser adapters, parser warnings, page/table metadata, and parser-quality evals. |
| Live database validation | JSON state is not enough for pilot readiness. | Run and document live Postgres/pgvector checks with RLS, migrations, indexes, pool behavior, and rollback. |
| Retrieval quality metrics | A working answer path does not prove retrieval quality. | Add recall@k, precision@k, citation-span accuracy, conflict/stale-source cases, and reranker comparison. |
| External observability | Local traces are not enough for operations. | Send SDK-level OpenTelemetry spans to Phoenix or another backend and link trace URLs in the UI. |
| Online eval loop | Static evals do not capture production drift. | Extend trace-to-eval into reviewed datasets, nightly regression, and human-label workflow. |
| Agent durability | Project 2 approval is useful, but real side effects need recovery. | Add workflow state, transactional outbox, idempotency keys, replay, and external connector dry-run mode. |
| Deployment operations | Production needs more than Docker files. | Add IaC/runbook/SLO/load test/backup/restore/rollback/alerting evidence. |

## Recommended Upgrade Sequence

1. Finish Project 1 data-plane hardening.
   - Real file upload endpoint.
   - One read-only source connector.
   - Incremental cursor and prune/delete behavior.
   - Parser job state and dead-letter records.
   - Postgres/pgvector live verification.

2. Add permission realism.
   - User/group/tenant model.
   - Source ACL mapping.
   - Permission drift tests.
   - RLS-backed denial count tests.

3. Improve retrieval evaluation.
   - Build a larger synthetic enterprise corpus.
   - Add queries for lookup, synthesis, conflict, stale-source, missing evidence, and permission denial.
   - Report recall@k, precision@k, faithfulness, citation-span accuracy, abstention correctness, and latency.

4. Add external observability.
   - OpenTelemetry SDK spans around request, retrieval, parsing, model, tool, approval, audit, and eval boundaries.
   - Phoenix or similar self-hosted backend.
   - Trace URL in UI and replay artifacts.

5. Turn trace-to-eval into an operations loop.
   - Human-reviewed candidate ledger.
   - Promotion status.
   - Nightly regression command.
   - Release gate comparing old/new model, prompt, retrieval, and reranker versions.

6. Harden Project 2 as the governed action layer.
   - Real connector dry-run.
   - Transactional outbox.
   - Idempotent execution.
   - Supervisor approval with durable workflow state.
   - Action rollback/compensation notes where possible.

7. Build one operator surface.
   - Sources and sync jobs.
   - Permissions and ACL drift.
   - Traces and eval candidates.
   - Approval queue.
   - Incidents and release gates.

## Product Direction

Do not try to make three unrelated demos production-ready in parallel. The strongest industrial story is:

```text
Enterprise AI Control Plane

source ingestion + source permission sync
  -> permission-aware RAG
  -> governed agent actions
  -> approval queue
  -> traces, audit, evals
  -> release gates and incident review
```

Project 1 should be the production data-plane backbone. Project 2 should become the governed side-effect layer. Project 3 should become the reliability and release-control layer.

This keeps the public story honest: the repo is not claiming to be production software today; it is showing the control boundaries that production software must preserve while the remaining infrastructure is upgraded.
