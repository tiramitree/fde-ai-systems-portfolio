# Industrialization Gap Plan

Date reviewed: 2026-06-06

This note answers one question:

> How far is this portfolio from a genuinely production-usable industrial AI system, and what should be upgraded next?

## Short Verdict

The repository is strong as an FDE technical review portfolio and reference implementation. It is not yet a production product.

Current maturity:

| Target | Readiness | Why |
| --- | --- | --- |
| Technical review portfolio artifact | High | It demonstrates real AI system boundaries: permissions, citations, abstention, approvals, traces, audit logs, evals, release blocking, CI gates, and public-repo hygiene. |
| Internal prototype / architecture demo | Medium | It can explain the control model and critical workflows, but it uses local deterministic data and local state. |
| Customer pilot with synthetic or limited data | Low-to-medium | It needs real auth, durable persistence, ingestion, cloud deploy, and monitored model runtime before a controlled pilot. |
| Production system over real enterprise data | Low | It lacks production data plane, identity, deployment, security operations, online monitoring, and connector lifecycle management. |

The most honest framing:

```text
This is not production software yet. It is a production-minded reference implementation that proves the right control boundaries before scaling the infrastructure around them.
```

## Industrial Baseline From Current Public References

Industrial-grade AI application projects repeatedly converge on the same components:

- Real retrieval stack: document ingestion, parsing, chunking, embeddings, vector/keyword search, reranking, citations, and access control.
- Durable runtime: database, migrations, queues, retries, idempotency, background jobs, and recovery after process restarts.
- Identity and authorization: real users, sessions, enterprise SSO, RBAC/ABAC, tenant isolation, and database-level policy.
- Agent governance: tool registry, tool permissions, dry-run mode, approval gates, sandboxing, audit logs, and connector-scoped credentials.
- Evaluation loop: golden datasets, adversarial cases, trace grading, regression gates, human labels, production feedback, and model/prompt comparison.
- Observability: traces, spans, model/tool/retrieval events, dashboards, cost/latency/error metrics, and production incident triage.
- Security and governance: OWASP LLM risk controls, prompt-injection testing, output validation, PII handling, retention, red-team workflows, and risk documentation.
- Deployment: cloud infrastructure, container images, secrets management, health/readiness checks, autoscaling, rollback, backup, and release runbooks.

Reference signals:

- Azure's RAG sample uses Azure AI Search, Azure OpenAI, cloud ingestion, optional Entra login/access control, Application Insights monitoring, deployment infrastructure, and cost guidance. It also warns that additional security work is required before production.
- AWS Generative AI Application Builder centers on managed dashboards for MCP servers, agents, multi-agent workflows, and RAG chatbot deployments.
- Dify combines AI workflow, RAG pipeline, agents, model management, integrations, and observability as one platform surface.
- RAGFlow emphasizes deep document understanding, complex unstructured formats, chunk visualization, grounded citations, multiple recall paths, reranking, and deployable Docker/self-hosting surfaces.
- Onyx emphasizes enterprise connectors and permission-aware retrieval; its GitHub connector specifically documents permission synchronization so users only see search results they are allowed to access in the source system.
- EnterpriseRAG-Bench simulates internal-company RAG over more than 500,000 documents and 500 questions, which is a useful scale marker for how far real enterprise retrieval differs from small demo seed data.
- OpenAI's current guidance treats evals as necessary because model behavior is variable, recommends building with the strongest model first to establish an accuracy baseline, and then optimizing with smaller models for cost and latency.
- OpenAI's agent safety guidance explicitly recommends tool approvals, guardrails, trace graders, evals, and keeping untrusted data from directly driving agent behavior.
- OpenTelemetry now has GenAI semantic conventions for model spans, agent spans, metrics, events, and provider-specific conventions.
- Phoenix/Langfuse-style platforms turn traces, evals, prompt versions, datasets, and annotations into the operational loop.
- LangGraph-style production agent systems treat checkpointing and persistence as core because crash recovery and human-in-the-loop workflows require durable state.
- OWASP and NIST frame the risk surface: prompt injection, insecure output handling, excessive agency, data leakage, and organizational risk management.

Source links reviewed on 2026-06-06:

- OpenAI eval best practices: https://developers.openai.com/api/docs/guides/evaluation-best-practices
- OpenAI agent build guide: https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/
- OpenAI agent safety: https://developers.openai.com/api/docs/guides/agent-builder-safety
- Onyx RAG and Search: https://docs.onyx.app/overview/core_features/internal_search
- Onyx GitHub connector permission sync: https://docs.onyx.app/admins/connectors/official/github
- EnterpriseRAG-Bench: https://github.com/onyx-dot-app/EnterpriseRAG-Bench
- RAGFlow: https://github.com/infiniflow/ragflow
- Phoenix: https://arize.com/docs/phoenix
- Langfuse: https://langfuse.com/docs
- LangGraph persistence: https://langgraphjs.guide/persistence/

## 2026-06 External Benchmark Snapshot

This snapshot was added after reviewing public production references, open-source
project surfaces, and current FDE / large-model application job descriptions on
2026-06-06. Star counts are volatile and should be treated only as a rough signal
of ecosystem weight, not quality by itself.

| Reference | Public signal | What it shows industrial teams care about |
| --- | --- | --- |
| OpenAI Deployment Company | OpenAI describes FDEs as engineers embedded with business leaders, operators, and frontline teams to redesign workflows and turn gains into durable systems. | The role is not just API wiring. It is workflow redesign, integration, deployment, and sustained operational ownership. |
| OpenAI production best practices | Production guidance emphasizes organization setup, latency, security, and robust architecture. | Production systems need operational controls around model calls, not just prompt quality. |
| OpenAI eval guidance | Guidance recommends continuous evaluation, production data, domain-expert cases, context recall, context precision, and answer quality metrics. | Evals must become a lifecycle, not a one-time test file. |
| OpenAI Agents tracing | Agents SDK tracing records generations, tool calls, handoffs, guardrails, and custom events for development and production monitoring. | Agent systems need traceable internal decisions and tool activity. |
| Azure Search OpenAI Demo | A real cloud RAG sample uses Azure AI Search and Azure OpenAI, while warning that extra security work is needed before production use. | Even polished vendor samples are still not production without security, access control, monitoring, and landing-zone hardening. |
| Dify | Publicly positions itself as a production-ready agentic workflow platform with workflows, RAG, integrations, model management, and observability. | Mature platforms bundle app building, RAG, tools, publishing, and observability in one operator surface. |
| Langfuse / Phoenix | Both center tracing, evals, prompt versions, datasets, experiments, annotations, and production trace scoring. | The eval/observability loop is a first-class product area. |
| Qdrant / Weaviate | Current docs emphasize hybrid search, staged retrieval, reranking, filters, and vector/keyword search combinations. | Industrial RAG is usually hybrid retrieval plus reranking and metadata filters, not vector-only search. |
| ByteDance Doubao FDE JD | Requires full-stack coding, LLM APIs, evaluation/performance methods, RAG, Agent, Workflow, and multi-agent implementation. | China FDE roles expect end-to-end build ability plus customer-facing solution design. |
| Alibaba Cloud model deployment JD | Emphasizes requirements discovery, architecture, data integration, RAG, Agent orchestration, model selection, usage monitoring, cost optimization, and best-practice output. | FDE success is judged by customer-perceived business value and repeatable methodology. |
| Lenovo AI FDE JD | Mentions private deployment, vLLM optimization, performance testing, stability, CUDA/CANN/GPU/container setup, RAG, tools, and agent workflow delivery. | Some China FDE roles are closer to field deployment plus infra troubleshooting, not only app-layer AI engineering. |
| SenseTime / enterprise agent JDs | Mention document parsing, retrieval algorithm optimization, Embedding/Reranker upgrades, Agentic RAG, automated eval sets, bad-case attribution, A/B tests, memory, and self-evolution. | Advanced industrial RAG work is about measurable quality iteration and failure analysis. |

Current ecosystem examples checked with GitHub metadata on 2026-06-06:

| Project | Stars checked | Main industrial lesson |
| --- | ---: | --- |
| `langgenius/dify` | 144099 | Unified workflow/RAG/agent/model-management surface matters. |
| `infiniflow/ragflow` | 82000+ | Complex document parsing, chunk visibility, citations, and reranking are production RAG differentiators. |
| `run-llama/llama_index` | 49947 | Document agents, parsing/OCR, and data connectors are a major layer by themselves. |
| `langchain-ai/langgraph` | 34018 | Durable, stateful, human-in-the-loop agent execution is a core production abstraction. |
| `microsoft/graphrag` | 33494 | Graph-augmented retrieval is used when flat chunks are not enough for enterprise reasoning. |
| `qdrant/qdrant` | 31848 | Search infrastructure and vector performance are their own production discipline. |
| `langfuse/langfuse` | 28572 | LLM observability, evals, prompt management, and datasets form an operational platform. |
| `deepset-ai/haystack` | 25466 | Modular pipelines with explicit retrieval/routing/generation control are production-oriented. |
| `weaviate/weaviate` | 16281 | Cloud-native vector DB plus structured filtering is part of the production data plane. |
| `Arize-ai/phoenix` | 10001 | OpenTelemetry-style tracing plus eval experiments are central to debugging AI apps. |
| `Azure-Samples/azure-search-openai-demo` | 7679 | Cloud RAG samples need identity, monitoring, deployment infrastructure, and security hardening before real use. |

Benchmark conclusion:

```text
Our repository is ahead of many portfolio projects on governance, eval gates,
public hygiene, and safety invariants. It is behind industrial systems on the
data plane, identity plane, runtime plane, observability backend, connector
lifecycle, deployment environment, and operational ownership model.
```

Distance estimate:

| Target | Approximate distance |
| --- | --- |
| FDE technical portfolio artifact | Very close. The repo already tells the right story and now has CI, docs, evals, governance, and repository boundaries. |
| Serious technical take-home / architecture review | Close. Add one production data-plane slice and the story becomes substantially stronger. |
| Controlled customer pilot with synthetic or low-risk data | Medium distance. Needs real auth, Postgres/pgvector runtime, parser/indexing pipeline, OTel backend, and one real connector. |
| Real enterprise production over sensitive data | Far. Needs tenant isolation, SSO, source permission sync, security operations, cloud IaC, backup/restore, incident runbooks, online evals, and support model. |

The next best decision is to avoid building more demos. The repository should
turn Project 1 into the production spine, then make Projects 2 and 3 operate as
the governed action layer and reliability layer around that spine.

## What This Repo Already Does Well

The repo is unusually strong for a portfolio demo in these areas:

| Area | Current Strength |
| --- | --- |
| Security boundary | The model is not treated as the security boundary. Permissions and side effects are enforced in application code. |
| RAG behavior | Project 1 proves role-filtered retrieval, citation-required answers, abstention, and prompt-injection handling. |
| Agent governance | Project 2 blocks direct side effects, creates approvals, requires supervisor execution, and records audit evidence. |
| Release reliability | Project 3 links incidents to failed eval evidence and blocks unsafe rollout. |
| Evals | There are deterministic golden evals across information disclosure, side-effect control, and release safety. |
| Observability shape | Traces, audit events, approvals, release decisions, and replay artifacts are connected. |
| Public hygiene | README, docs, release, branch protection, CI, issue templates, PR policy, screenshots, and launch assets are in place. |
| Local reliability | The project runs without paid APIs and has a strong local quality gate. |

This is the right foundation. The missing work is mostly replacing local/synthetic surfaces with production infrastructure and real integration boundaries.

## Major Gaps To True Industrial Usability

### 1. Real Data Ingestion And Retrieval

Current state:

- Small fictional seed data.
- Deterministic retrieval logic.
- No file upload, background parser pipeline, production embedding provider, live vector DB validation, production reranker provider, connector sync, or incremental indexing.

Industrial requirement:

- File upload and source connectors for Google Drive, Confluence, Slack, Notion, GitHub, Jira, S3, SharePoint, email, CRM, and ticketing systems.
- Parser pipeline for PDFs, Office files, tables, scanned documents, images, and mixed-layout documents.
- Chunking strategy with metadata, ACLs, source spans, page/section references, and versioning.
- Hybrid retrieval: lexical search plus vector search plus reranking.
- Retrieval evals: recall@k, citation faithfulness, answer correctness, abstention correctness, stale-source detection, and permission-leak detection.

Upgrade:

```text
Add ingestion worker -> document parser -> chunk store -> embedding job -> pgvector/search index -> hybrid retrieval -> reranker -> citation spans.
```

### 2. Identity, Tenancy, And Authorization

Current state:

- User roles are fictional and selected in the UI.
- Authorization is enforced in code but not tied to real identity.

Industrial requirement:

- Login via enterprise identity provider.
- Tenant isolation.
- RBAC/ABAC policy model.
- Database row-level security as defense in depth.
- Permission sync from source systems.
- User/session audit trails.

Upgrade:

```text
Add auth middleware, tenant context, policy engine, row-level security, and permission-sync tests.
```

### 3. Durable State And Workflow Runtime

Current state:

- Local JSON/runtime state is enough for demos.
- No production DB adapter, queues, recovery, or long-running workflow engine.
- A first PostgreSQL/pgvector migration artifact now exists at `infra/postgres/migrations/001_core.sql` and is guarded by `python -B scripts/dev.py postgres-migrations`.
- A deterministic Project 1 demo seed SQL artifact now exists at `infra/postgres/seeds/001_project1_demo.sql` and is guarded by `python -B scripts/dev.py postgres-seed`.
- Project 1 application modules now depend on `KnowledgeRepository` in `secure-enterprise-knowledge-copilot/src/copilot/repositories.py` instead of directly depending on JSON state internals.
- Project 1 now also has an optional `PostgresKnowledgeRepository` adapter contract in `secure-enterprise-knowledge-copilot/src/copilot/postgres_repositories.py`, covering tenant context, documents, chunks, SQL-backed keyword/vector retrieval candidates, denied-evidence counts, traces, audit events, and eval runs without making PostgreSQL required for the local demo. The shared retrieval path now also has a deterministic reranker boundary for feature-level post-retrieval scoring.

Industrial requirement:

- PostgreSQL for application state.
- Migrations.
- Transactional audit writes.
- Redis or queue-backed workers.
- Transactional outbox for external side effects.
- Idempotency keys for every irreversible action.
- Long-running agent/workflow checkpoints.

Upgrade:

```text
Wire the existing repository interface and PostgreSQL adapter contract to a real connection pool; add remaining backfill scripts, outbox, worker queue, and crash-recovery tests.
```

### 4. Model Runtime And Prompt/Policy Versioning

Current state:

- Local deterministic mode is the verified default.
- Optional OpenAI path exists for model-facing behavior.
- The docs still need to be updated from `gpt-5.2` to current `gpt-5.5` if this becomes the target model.

Industrial requirement:

- Model gateway with model selection by task.
- Structured outputs everywhere.
- Prompt/policy versioning.
- Model snapshot pinning where behavior stability matters.
- Streaming support.
- Retries, timeouts, circuit breakers, rate-limit handling.
- Cost and latency budgets.
- Prompt caching and response caching where safe.

Upgrade:

```text
Use GPT-5.5 for complex reasoning and GPT-5.4-mini or smaller models for low-risk routing; record model, prompt version, policy version, token counts, latency, and cost in each trace.
```

### 5. Agent Tooling And Connectors

Current state:

- Tools are local deterministic functions.
- Approval model is good, but connectors are fictional.

Industrial requirement:

- Real tool registry with schemas.
- Connector credentials scoped per tenant and action.
- External systems: CRM, ticketing, email, calendar, Slack/Teams, incident tools, GitHub/Jira/Linear.
- Dry-run mode and preview diffs for side effects.
- Human approval queues with ownership, escalation, expiry, and audit.
- Sandbox for code or shell-like tools.

Upgrade:

```text
Build one real connector path end-to-end, but keep all external state-changing tools behind the same deterministic approval middleware.
```

### 6. Observability And Evaluation Operations

Current state:

- Local traces and OTLP-shaped export exist.
- Evals are deterministic and run in CI.

Industrial requirement:

- Native OpenTelemetry SDK instrumentation.
- GenAI semantic conventions for model, retrieval, tool, agent, and MCP spans.
- Trace backend such as Phoenix, Langfuse, Arize, Grafana, Honeycomb, or vendor APM.
- Online evals from traces.
- Human annotation queue.
- Failure clustering and eval-case promotion.
- Regression dashboard by release, source, tenant, model, prompt, tool, and risk category.

Upgrade:

```text
Emit OTel spans in live requests, ingest them into Phoenix/Langfuse, add trace grading, and create an eval dataset from real or simulated production failures.
```

### 7. Security, Privacy, And Compliance

Current state:

- Strong public-repo hygiene and clear threat model.
- Prompt-injection and unsafe-side-effect tests exist.

Industrial requirement:

- OWASP LLM Top 10 test suite.
- PII detection and redaction.
- Data retention and deletion policy.
- Encryption at rest and in transit.
- Secrets manager.
- Security review for every connector.
- Audit retention and immutability.
- Abuse/rate-limit controls.
- Red-team exercises and incident response.
- NIST AI RMF mapping for governance language.

Upgrade:

```text
Turn the threat model into a security control matrix with tests, owners, logs, retention, and incident runbooks.
```

### 8. Deployment, Scale, And Reliability

Current state:

- Dockerfiles and compose are checked.
- Runtime is local-first.

Industrial requirement:

- Cloud deployment with IaC.
- Separate API, worker, frontend, DB, vector/search, and observability services.
- Health/readiness checks.
- Autoscaling and resource limits.
- Backup/restore.
- Blue/green or canary releases.
- Rollback runbooks.
- Load tests and latency budgets.

Upgrade:

```text
Add a deployable reference stack: FastAPI service, Postgres/pgvector, Redis worker, OTel collector, and a managed frontend behind an API gateway.
```

### 9. Product Surface And Admin UX

Current state:

- UI demonstrates workflows.
- No real admin or operator surface.

Industrial requirement:

- Source connection management.
- Permission audit UI.
- Eval dashboard.
- Prompt/model configuration UI.
- Approval queue with assignment and escalation.
- Trace explorer.
- Incident and release dashboards.
- Tenant settings.

Upgrade:

```text
Keep the current three demos, but add one unified admin console that shows sources, evals, traces, approvals, and release gates.
```

## Recommended Upgrade Strategy

Do not try to industrialize all three projects equally. That would produce a wide but shallow system.

Best path:

1. Make Project 1 the real production-grade core: enterprise knowledge access with permissions, citations, ingestion, evals, and observability.
2. Attach Project 2 as the governed action layer: selected tools can act on retrieved/operational context, but approval gates remain deterministic.
3. Keep Project 3 as the reliability and eval operations console: it monitors the first two systems rather than feeling like a separate toy app.

Target product shape:

```text
Enterprise AI Control Plane

Sources + permissions
  -> RAG retrieval with citations
  -> governed agent actions
  -> approval queue
  -> traces and audit
  -> eval regression console
  -> release gates
```

This is a much stronger story than "three separate demos."

## Concrete Build Plan

### Phase A: Production Skeleton

Deliverables:

- FastAPI service boundary.
- PostgreSQL with migrations.
- Repository interfaces for documents, chunks, users, traces, audit, approvals, evals.
- Redis worker queue.
- OTel SDK instrumentation.
- Docker Compose production-like stack.
- Environment and secret handling.
- Load-test baseline.

Exit criteria:

- One command starts API, DB, worker, OTel collector, and frontend.
- All current smoke/eval tests still pass.
- Trace IDs connect UI, logs, DB, and OTel spans.

### Phase B: Real RAG Data Plane

Deliverables:

- File upload.
- Parser pipeline for PDF, DOCX, Markdown, CSV, HTML.
- Chunking and metadata strategy.
- Embeddings and pgvector/search indexes.
- Hybrid retrieval and reranking.
- Source citation spans.
- ACL filters before retrieval result assembly.

Exit criteria:

- Upload a document, index it, ask questions, cite exact chunks, abstain when permission/evidence is missing.
- Permission-leak evals still pass.
- Retrieval recall and answer faithfulness have measurable evals.

### Phase C: Governed Agent Runtime

Deliverables:

- Tool registry.
- Tool schemas.
- One real external connector.
- Dry-run previews.
- Approval queue with ownership, expiry, and idempotency.
- Transactional outbox.
- Tool-call trace spans.

Exit criteria:

- The agent can propose an external action.
- The system records a preview.
- A supervisor approves.
- The side effect executes once.
- Duplicate approval or bypass attempts are blocked and auditable.

### Phase D: Evaluation And Observability Loop

Deliverables:

- Phoenix or Langfuse integration.
- Trace grading for tool choice, citation faithfulness, approval compliance, and safety policy violations.
- Human annotation queue.
- Eval dataset versioning.
- CI gate plus optional nightly eval batch.
- Cost, latency, token, and retrieval metrics.

Exit criteria:

- A bad production-like trace can be promoted into an eval case.
- Prompt/model changes can be compared before release.
- Release gates fail on unsafe leaks, unsupported answers, and unsafe side effects.

### Phase E: Security And Governance Hardening

Deliverables:

- OWASP LLM Top 10 mapped tests.
- PII redaction.
- Data retention controls.
- Secrets manager integration.
- Connector credential scoping.
- Audit retention and export.
- NIST AI RMF mapping.
- Security runbook.

Exit criteria:

- A reviewer can map each major AI risk to code, logs, tests, and operational owner.
- Sensitive data paths are controlled and documented.

### Phase F: Production Deployment

Deliverables:

- IaC for one cloud target.
- API gateway.
- Auth integration.
- Managed DB.
- Managed vector/search.
- OTel collector and dashboard.
- Backup/restore.
- Release rollback.
- Runbook for common failures.

Exit criteria:

- A clean environment can be provisioned, smoke-tested, monitored, and rolled back.
- Deployment evidence is captured in docs and CI.

## Technical Review Framing

Use this:

```text
The repository is deliberately not claiming to be production software. It is a production-minded reference implementation. I built the control boundaries first: permissions before generation, citations and abstention, approval gates before side effects, eval regression gates, trace/audit evidence, and release blocking. To make it industrial, I would replace the local data plane with authenticated multi-tenant Postgres/pgvector, real ingestion/connectors, OTel traces into an observability backend, online evals from traces, and cloud deployment with secrets, queues, rollback, and security controls. The key point is that the production upgrade should preserve the current invariants, not move them into prompts.
```

## Priority Order

If only one improvement can be made, do real RAG ingestion and pgvector with permissions.

If two improvements can be made, add OTel + Phoenix/Langfuse trace and eval loop.

If three improvements can be made, add one real governed connector with approval and idempotent execution.

Those three upgrades would move the repo from "excellent portfolio demo" to "credible pilot architecture."
