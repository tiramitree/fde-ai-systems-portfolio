# Industrial Readiness Field Scan

Date reviewed: 2026-06-06

This note records the current industrial-readiness judgment after comparing the
portfolio against current public production-oriented RAG, agent, observability,
and AI risk references. It is meant to guide the next implementation steps, not
to claim the repository is production software.

## Short Verdict

The repository is close to an excellent FDE technical-review and architecture-review
artifact. It is still far from a real industrial product over sensitive
enterprise data.

| Target | Current distance | Judgment |
| --- | --- | --- |
| FDE portfolio / technical storytelling | Close | The project already demonstrates the right control boundaries: permissions before generation, citations, abstention, approvals, traces, audit, evals, release gates, public CI, and documentation. |
| Serious take-home / system-design review | Close to medium | The architecture is credible, but reviewers will expect one production data-plane slice to be live, not only documented. |
| Controlled internal pilot on low-risk data | Medium to far | Needs real auth, durable Postgres/pgvector runtime, ingestion/parser/embedding pipeline, external observability, and at least one real connector. |
| Production over real enterprise data | Far | Needs enterprise identity, source permission sync, tenant isolation, security operations, online evals, backups, incident runbooks, deployment, and support ownership. |

The honest framing remains:

```text
This is a production-minded reference implementation. It proves the application
controls that production AI systems need, but it does not yet provide the full
production data plane, identity plane, runtime plane, observability backend, or
operations model.
```

## External Baseline

The public industrial projects and references cluster around the same patterns:

| Reference | Relevant signal | What it means for this repo |
| --- | --- | --- |
| Dify | Public repo positions it as a production-ready agentic workflow platform with workflow, RAG pipeline, agent capabilities, model management, observability, APIs, Docker Compose, Kubernetes, and cloud deployment paths. Source: https://github.com/langgenius/dify | A mature product gives operators a whole platform surface, not just three demos. We need a unified operator/admin surface eventually. |
| RAGFlow | Emphasizes deep document understanding, explainable chunking, grounded citations, heterogeneous data sources, multiple recall, and fused reranking. Source: https://github.com/infiniflow/ragflow | Project 1 needs real parsing, chunk visualization or auditability, hybrid retrieval, reranking, and robust citation spans. |
| Onyx | Enterprise connectors include permission synchronization so search results match source-system access control. Source: https://docs.onyx.app/admins/connectors/official/github | Role-aware demo users are not enough. The production path needs permission sync from source systems. |
| EnterpriseRAG-Bench | Uses more than 500,000 internal-company documents across Slack, Gmail, Linear, Drive, HubSpot, meetings, GitHub, Jira, and Confluence with 500 questions across reasoning categories. Source: https://github.com/onyx-dot-app/EnterpriseRAG-Bench | Our seed corpus is tiny. Real enterprise RAG must handle volume, noise, conflicts, stale facts, metadata, and "not found" cases. |
| Langfuse | Centers LLM observability, traces, evals, prompt management, datasets, and production debugging. Source: https://github.com/langfuse/langfuse | Local traces are a good shape, but industrial systems need an external trace/eval operations loop. |
| Phoenix | Frames AI observability around traces, output scoring, production examples, prompts, and experiments. Source: https://arize.com/docs/phoenix | We need trace promotion into evals and experiment comparison, not just static golden cases. |
| LangGraph | Persistence saves graph state as checkpoints and enables human-in-the-loop, memory, time travel, and fault-tolerant execution. Source: https://docs.langchain.com/oss/python/langgraph/persistence | Project 2 approvals need durable workflow state and crash recovery before real external actions. |
| OpenAI Agents SDK | HITL pauses execution until sensitive tool calls are approved or rejected; tracing records LLM generations, tool calls, handoffs, guardrails, and custom events. Sources: https://openai.github.io/openai-agents-python/human_in_the_loop/ and https://openai.github.io/openai-agents-python/tracing/ | Our approval and trace ideas are aligned with modern agent practice, but should become durable and externally observable. |
| OWASP LLM Top 10 | Highlights prompt injection, insecure output handling, sensitive information disclosure, plugin/tool risk, excessive agency, and overreliance. Source: https://owasp.org/www-project-top-10-for-large-language-model-applications/ | Existing threat-model work should become a mapped AI security test suite. |
| NIST AI RMF | Positions trustworthiness considerations as part of design, development, use, and evaluation of AI systems. Source: NIST AI Risk Management Framework. | The final industrial story needs governance language, ownership, monitoring, and lifecycle controls. |

## Current Strengths

The repo is stronger than a normal portfolio demo in these areas:

- It treats the model as untrusted and keeps security decisions in application code.
- Project 1 filters by tenant/role before evidence reaches the answer layer.
- Project 1 records citations, abstentions, prompt-injection handling, traces, audit events, and evals.
- Project 2 has deterministic approval gates before side effects.
- Project 3 connects eval failures to release-blocking decisions.
- CI and local quality gates protect public claims, screenshots, docs, evals, and runtime contracts.
- The current PostgreSQL/RLS work is moving Project 1 from local-state demo toward a real data-plane adapter.

## Main Gaps

| Area | Current gap | Industrial requirement |
| --- | --- | --- |
| Data ingestion | Fictional seed data and deterministic local ingestion. | Uploads, connector sync, document parsing, OCR/table handling, incremental indexing, source versioning, and backfills. |
| Retrieval quality | Local deterministic embeddings, vector score reporting, and optional PostgreSQL keyword/vector candidate selection now exist, but the path is still pre-reranker and not live-validated against a large corpus. | Production embeddings, hybrid search metrics, pgvector/search backend validation, reranker, recall/precision evals, citation span checks, stale-source handling. |
| Source permissions | UI-selected fictional users and roles. | Enterprise SSO, tenant isolation, source ACL sync, RBAC/ABAC, database RLS, permission-drift tests. |
| Runtime durability | Local JSON path remains default; Postgres path is in progress. | Migrations, connection pooling, durable audit/traces, queues, retries, transactional outbox, crash recovery. |
| Agent workflow | Deterministic local tools and approvals. | Real tool registry, scoped credentials, dry-run previews, approval ownership, expiry, idempotent execution, connector failure handling. |
| Observability | Local trace shape and OTLP-like export. | OpenTelemetry SDK spans, Phoenix/Langfuse or equivalent backend, dashboards, online evals, cost/latency/error metrics. |
| Evaluation | Deterministic golden evals. | Production trace sampling, human labels, red-team packs, model/prompt comparison, failure clustering, nightly regression batches. |
| Security | Good threat model and safety checks. | OWASP-mapped tests, PII redaction, secret management, data retention/deletion, immutable audit, incident response. |
| Deployment | Local-first Python services and static config checks. | Cloud IaC, auth gateway, managed DB/search, worker fleet, health/readiness, backups, rollbacks, load tests. |
| Admin/operator UX | Three separate demo UIs. | Unified admin surface for sources, permissions, evals, traces, approvals, incidents, and release gates. |

## Recommended Product Direction

Do not industrialize the three demos equally. That would create breadth without
depth.

Recommended direction:

```text
Project 1 becomes the production spine:
  enterprise knowledge ingestion, permissions, retrieval, citations, abstention,
  traces, audit, and evals.

Project 2 becomes the governed action layer:
  real tools can act on operational context, but preview, approval, idempotency,
  and audit stay deterministic.

Project 3 becomes the reliability layer:
  eval regressions, incidents, trace failures, and rollout decisions become one
  release-control surface.
```

Target product shape:

```text
Enterprise AI Control Plane

sources + permission sync
  -> ingestion/parser/indexing pipeline
  -> permission-aware RAG
  -> governed agent actions
  -> approval queue
  -> traces, audit, evals
  -> release gates and incident review
```

## Execution Plan

This is ordered by technical-review value and industrial value.

1. Finish and verify the current Project 1 PostgreSQL/RLS slice.
   - Keep the local JSON path as the default.
   - Make Postgres opt-in through `COPILOT_REPOSITORY=postgres`.
   - Run the static gates and, on a Docker-enabled machine, the live Postgres/RLS check.
   - The key proof is: Alice cannot retrieve finance content, Morgan can, and denied relevant evidence is counted without leaking unauthorized content.

2. Add a production-like Project 1 data plane.
   - File upload.
   - Parser pipeline for Markdown, TXT, CSV, HTML, DOCX, and PDF.
   - Chunk metadata with source URI, source version, title, section, page/span when available, tenant, and ACL.
   - Embedding job and pgvector index.
   - Hybrid lexical + vector retrieval with reranking.

3. Add retrieval quality evals.
   - Recall@k for expected source chunks.
   - Faithfulness and citation coverage.
   - Abstention correctness.
   - Permission-leak cases.
   - Conflicting-info and stale-source cases.
   - Metadata-dependent cases.

4. Add identity and permission sync.
   - Start with a local enterprise-auth stub rather than a full SSO rollout.
   - Model tenant, user, group, source ACL, and role policy separately.
   - Add source permission-sync fixtures for one connector.
   - Keep Postgres RLS as defense in depth.

5. Add external observability.
   - Emit real OpenTelemetry spans for API, retrieval, model, tool, approval, audit, and eval events.
   - Send traces to Phoenix or Langfuse.
   - Preserve local trace IDs so UI output links to backend traces.

6. Add trace-to-eval workflow.
   - Let a failed trace become a new eval case.
   - Version the eval dataset.
   - Compare model/prompt/retrieval changes before release.
   - Track cost, latency, token use, and failure class.

7. Add one read-only connector.
   - Best candidates: GitHub issues/PRs, Google Drive, or local S3-style object storage.
   - Start read-only to avoid side-effect risk.
   - Include source permissions, incremental sync, connector health, and backfill logs.

8. Add one governed write connector.
   - Best candidates: GitHub issue comment, Jira/Linear ticket update, or CRM note draft.
   - Require dry-run preview, approval, idempotency key, outbox, audit event, and retry policy.

9. Build the unified operator surface.
   - Sources and sync status.
   - Permission audit.
   - Retrieval/eval dashboard.
   - Trace explorer links.
   - Approval queue.
   - Release gate and incident state.

10. Add security hardening.
    - OWASP LLM Top 10 mapping.
    - Prompt-injection and indirect-injection cases from retrieved content.
    - PII redaction before model calls and trace export.
    - Data retention/deletion plan.
    - Secrets manager integration.
    - Connector credential scoping.

11. Add production deployment.
    - API service, worker, frontend, Postgres/pgvector, Redis or queue, OTel collector.
    - Docker Compose as local production-like stack.
    - One cloud IaC target after local stack is stable.
    - Backup/restore, health checks, canary/rollback, and load test baseline.

12. Add operational runbooks.
    - Ingestion failure.
    - Permission drift.
    - Retrieval quality regression.
    - Model cost spike.
    - Tool approval backlog.
    - Connector outage.
    - Unsafe trace or incident.

## What Not To Claim Yet

Do not claim these until the matching evidence exists:

- "Production-ready" for real customer data.
- "Enterprise secure" beyond the current demo threat model.
- "Scales to enterprise corpora" before testing larger corpora and ingestion jobs.
- "Live OpenAI production mode" before live API checks pass in an API-key environment.
- "Docker/Postgres runtime verified" before a Docker-enabled live check passes.
- "Permission sync" before a source connector proves ACL import and enforcement.
- "Observability platform integrated" before traces land in Phoenix/Langfuse or another backend.

## Technical Review Framing

Use this explanation:

```text
I built this as a production-minded reference, not as a fake production claim.
The core value is that the model is not the security boundary: permissions,
side effects, citations, abstention, approvals, evals, trace IDs, and release
gates are all enforced by application code. The next industrial step is to make
Project 1 the production spine with Postgres/pgvector, real ingestion,
permission sync, external observability, and retrieval evals. Then Project 2
becomes the governed action layer and Project 3 becomes the reliability layer.
That upgrade preserves the current invariants while replacing local demo
surfaces with production infrastructure.
```

## Highest Leverage Next Move

The next best engineering move is not another demo. It is:

```text
Finish the Project 1 Postgres/RLS path, then add one real ingestion + retrieval
path with parser, chunks, embeddings, pgvector, hybrid retrieval, citations,
permission checks, and evals.
```

That single slice would move the repository from "excellent portfolio demo" to
"credible controlled-pilot architecture."
