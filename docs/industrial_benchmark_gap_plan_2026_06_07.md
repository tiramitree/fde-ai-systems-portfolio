# Industrial Benchmark Gap Plan

Date: 2026-06-07

This note records the current external benchmark scan and the concrete upgrade
plan for moving the repository from a strong FDE portfolio reference
implementation toward a genuinely industrial AI system. It is deliberately
strict: the project is already unusually complete for a public portfolio, but
it is not yet production software for sensitive enterprise data.

## Executive Judgment

Current honest positioning:

```text
Production-minded reference implementation.
```

Do not claim:

```text
Production-ready enterprise AI platform.
```

The repository already proves the right control boundaries:

- permission filtering before generation, including source-group identity checks in Project 1
- grounded citations and abstention
- prompt-injection handling in retrieved context
- admin ingestion and connector-style source sync
- connector job ledger, retry lineage, dead letters, status, and opt-in prune
- governed tool actions and approval queues
- trace, audit, eval, release gate, and CI evidence
- public GitHub safety and maintenance hygiene

The remaining gap is not a missing UI button. The missing part is the industrial
data plane, identity plane, runtime plane, observability plane, and operations
model that would make the same invariants hold under real traffic, real source
systems, real users, and real failures.

## Distance Estimate

| Target | Current distance | Current maturity | Honest judgment |
| --- | --- | --- | --- |
| FDE portfolio / technical review artifact | Close | 85%-90% | Strong enough to discuss architecture, tradeoffs, security boundaries, evals, and public maintenance. |
| Serious architecture review / take-home | Close to medium | 75%-82% | Credible, especially after ingestion jobs, connector status, and source prune semantics. Reviewers will still ask for live identity, source APIs, and durable workers. |
| Controlled demo with synthetic data | Close | 65%-75% | Strong local demo and CI story. It can show many production invariants without exposing private data. |
| Low-risk internal pilot | Medium to far | 35%-45% | Needs real auth, durable Postgres/pgvector, parser workers, live connectors, external observability, and operator runbooks. |
| Sensitive enterprise production | Far | 20%-30% | Needs SSO, tenant isolation, source ACL sync, data retention/deletion, incident response, security ops, cloud deployment, backup/restore, load tests, and owner model. |

## 2026 Web Scan Calibration

This refresh looked at current production-oriented RAG, agent, LLMOps,
governance, and Chinese/China-adjacent open-source AI platform references. The
shared pattern is clear: industrial systems are not better because they have a
flashier chat UI. They are better because they operate an end-to-end control
plane around messy data, real identities, real tools, traceable quality, and
operator recovery.

| Source family | Public signal | Industrial meaning for this repo |
| --- | --- | --- |
| RAGFlow | Current RAGFlow positions itself as an enterprise RAG engine with agent capabilities, deep document understanding, template chunking, grounded citations, heterogeneous data sources, multiple recall, fused reranking, self-hosting, and recent support for source sync, agentic workflow, MCP, memory, code execution, Docling/MinerU, multimodal document understanding, DeepSeek, Gemini, and GPT-5-series models. | Project 1 has the right control shape, but industrial RAG needs serious parsing, source spans, visual/auditable chunking, retrieval profiles, reranking, broad source connectors, and deployment resources. |
| Dify Enterprise | Dify emphasizes develop/deploy/manage agents and RAG pipelines for teams, unified knowledge hub, autonomous agents, enterprise-grade security/access controls, high availability, and on-prem/public-cloud/VPC deployment. | A true product needs an admin/operator platform, deployment posture, access control, and team workflow management, not only isolated demos. |
| FastGPT | FastGPT markets itself as an enterprise AI productivity engine and open-source RAG/agent platform with secure, controllable enterprise-grade AI agents, production-proven private deployments, and enterprise customization. | China-market FDE value depends on business integration speed, controllable workflow delivery, private deployment, and customer-visible reliability. |
| MaxKB | MaxKB is an open-source enterprise agent platform with RAG pipelines, robust workflows, MCP tool-use support, multimodal input/output, model-agnostic support, Docker startup, Django/Vue, PostgreSQL, and pgvector. | A production-shaped portfolio should show framework-independent model/runtime choices, one-command deployment, and an industrial data store. |
| EnterpriseRAG-Bench | EnterpriseRAG-Bench uses about 512k synthetic enterprise documents across Slack, Gmail, Linear, Google Drive, HubSpot, Fireflies, GitHub, Jira, and Confluence, with 500 questions over 10 categories including multi-document reasoning, constrained retrieval, conflicts, noise, near-duplicates, and absence detection. | The current corpus is tiny. The next credibility jump is not more UI polish; it is large/noisy enterprise-style retrieval evaluation. |
| LangChain 2026 agent survey | LangChain reports production agent momentum, with quality as a major production blocker, observability near table-stakes adoption, and eval adoption lagging observability. | Our trace/eval story is pointed in the right direction, but industrial credibility requires online observability, failure clustering, and trace-to-eval operations. |
| LangSmith | LangSmith frames production agent engineering around full-step tracing, monitoring, alerts, evaluations, deployment, enterprise security/compliance, self-hosting, and fast iteration. | Local traces must become external traces with metrics, alerts, labels, and eval dataset feedback. |
| LangGraph | LangGraph persistence/checkpointing is required for human-in-the-loop, memory, time travel debugging, and fault-tolerant execution; interrupts pause and continue with durable state. | Project 2 approvals are conceptually correct, but industrial action agents need persisted workflow checkpoints and restart-safe execution. |
| OpenAI Evals and business eval guidance | OpenAI describes evals as the way to make LLM applications stable across code/model changes, and stresses that frontier evals do not replace contextual evals for a specific business workflow. | The repo's golden evals should expand into business-specific regression sets, retrieval metrics, trace grading, human labels, and model/prompt comparison. |
| OpenAI Agents SDK guardrails | Tool guardrails can run before/after function tools and trip execution, but not every hosted/built-in/handoff path is covered by the same guardrail pipeline. | Do not delegate safety to SDK abstractions alone. Keep application-level policy, approval, and audit boundaries explicit. |
| OpenTelemetry GenAI conventions | OTel now defines GenAI span, event, metric, and attribute conventions, including token usage and model-operation telemetry. | Move from ad hoc local trace JSON toward OTel-compatible spans for API, retrieval, model, tool, approval, audit, eval, and release decisions. |
| OWASP Agentic Applications Top 10 | OWASP's 2026 agentic framework targets autonomous systems that plan, act, and make decisions across complex workflows. | Project 2 and Project 3 need explicit tests against tool misuse, identity/privilege abuse, context poisoning, cascading failure, and trust exploitation. |
| NIST AI RMF and GenAI Profile | NIST frames AI risk management across design, development, use, evaluation, governance, measurement, and management. | Add risk ownership, residual risk, retention/deletion, incident response, monitoring, and release accountability evidence. |

## Distance From Truly Industrial Use

Current judgment after this scan:

```text
The project is close to an excellent FDE portfolio and architecture artifact.
It is still far from a true industrial product over sensitive enterprise data.
```

Approximate gap:

- FDE technical-review signal: small gap. The repository already demonstrates unusually
  strong enterprise AI judgment.
- Architecture review credibility: medium gap. It can explain the right
  production invariants, but reviewers can still ask for real source systems,
  real identity, and live operational evidence.
- Controlled pilot: large gap. It needs real auth, durable runtime, real
  connector sync, scale tests, and external observability.
- Sensitive production: very large gap. It needs enterprise security,
  compliance, deployment, support ownership, incident response, and operational
  maturity.

The shortest honest phrase remains:

```text
Production-minded reference implementation, not production software.
```

## External Baseline Scan

| Reference | Industrial signal | Implication for this repo |
| --- | --- | --- |
| OpenAI production best practices | Production systems need staging/production isolation, rate/spend limits, access control, monitoring, and scale planning. | Add explicit provider budget/rate-limit controls, environment isolation, and live-mode safety evidence before any production claim. |
| OpenAI eval guidance | Evals should be task scoped, continuous, log-driven, and calibrated with human feedback; Q&A over docs should track context recall, precision, and answer satisfaction. | Expand current deterministic evals into retrieval metrics, trace-derived eval cases, human review disposition, and nightly regression. |
| OpenAI trace grading | Graded traces help evaluate agent decisions, tool calls, and workflow behavior beyond black-box outputs. | Promote bad traces into eval candidates and grade retrieval/tool/approval decisions, not only final answer text. |
| OpenAI Agents SDK tracing and HITL | Production agent runs trace generations, tools, handoffs, guardrails, and custom events; sensitive tools can pause, serialize state, and continue after approval. | Project 2 is directionally right, but needs persisted run state, idempotent execution, approval expiry/ownership, and real connectors. |
| Microsoft Azure RAG design guide | Industrial RAG requires representative test media/queries, chunking strategy, metadata enrichment, embedding choice, index configuration, search strategy, and evaluation at every stage. | Project 1 needs a real parser/chunk/embed/index path with measured retrieval and citation quality. |
| AWS Generative AI Application Builder and Well-Architected GenAI Lens | Enterprise GenAI stacks include management dashboards, RAG, agents, guardrails, observability, security, reliability, cost, and deployment architecture. | A unified operator console and deployment/runtime plan matter as much as the model-facing app. |
| Dify | Production-oriented LLM app platforms bundle workflows, RAG pipelines, integrations, model management, and observability. | The repo should converge from three isolated demos into one "Enterprise AI Control Plane" story. |
| RAGFlow | Mature RAG engines emphasize deep document understanding, explainable chunking, heterogeneous data sources, grounded citations, multiple recall, and reranking. | Add document parsing, source spans, table/PDF strategy, hybrid retrieval, reranker, and citation span verification. |
| Onyx | Enterprise search/RAG centers on connectors, near-real-time indexing, document metadata, and source permission sync. | Strengthen GitHub read connector first, then add one or two high-signal enterprise sources with ACL snapshots and live deletion/prune proof. |
| Langfuse and Phoenix | LLMOps platforms combine traces, metrics, datasets, experiments, prompt management, user feedback, and evals. | Local traces should export to a backend and drive eval datasets, not remain only local JSON evidence. |
| LangGraph / durable agent runtimes | Long-running and human-in-the-loop agents require persistence, checkpoints, and restart-safe continuation. | Approval flows must survive process restarts and continue safely from persisted state. |
| OpenTelemetry GenAI conventions | GenAI observability now has model, agent, event, metric, and provider-specific semantic conventions. | Replace ad hoc trace-only claims with OTel spans for API, retrieval, model, tool, approval, audit, and eval events. |
| OWASP LLM Top 10 | Prompt injection, sensitive information disclosure, vector/embedding weakness, insecure plugins, and excessive agency are core LLM app risks. | Convert the current threat model into an OWASP-mapped control matrix with tests, owners, and runbooks. |
| NIST AI RMF and GenAI Profile | Industrial AI governance requires risk framing, measurement, management, documentation, and accountability. | Add governance evidence: risk ownership, residual risk, data retention, incident process, and release accountability. |
| Alibaba Bailian / Baidu Qianfan / Volcengine Coze enterprise docs | Chinese enterprise platforms expose RAG, Agent, workflow, knowledge base, model operations, observability/evaluation, and permission surfaces. | The China-market FDE narrative should emphasize business-system integration, workflow delivery, private data governance, and operator-facing deployment. |

## Current Strengths

| Area | Current repository evidence |
| --- | --- |
| Security invariant | The model is not treated as a security boundary; app code enforces permissions, source-group ACL checks, and side-effect gates. |
| RAG behavior | Project 1 supports permission-aware retrieval, citations, abstention, prompt-injection handling, admin ingestion, connector source sync, source lifecycle filtering, job status, and opt-in source prune. |
| Connector operations | Project 1 now includes a GitHub read connector contract, ingestion job ledger, idempotency, retry parent, dead-letter records, connector status, and prune semantics. |
| Agent governance | Project 2 blocks direct side effects and requires supervisor approval for sensitive operations. |
| Reliability workflow | Project 3 links failed eval evidence to release blocking and incident triage. |
| Public maintainability | The repo has README, case studies, threat model, API docs, screenshots, CI, PR policy, public-safety scan, and GitHub maintenance docs. |
| Upgrade path | Postgres/pgvector schema, RLS artifacts, repository interfaces, model gateway boundaries, OTLP-shaped export, and quality gates are already present. |

## Eight Industrial Gaps

| Gap | Current state | Industrial target |
| --- | --- | --- |
| 1. Data ingestion and parsing | Seed data, admin ingestion, source sync, GitHub read connector, job ledger, status, and opt-in prune. | Upload/pull connectors for real docs, parser worker, OCR/table/PDF/DOCX/CSV handling, source versions, source hashes, incremental sync, live prune/delete verification, and backfill recovery. |
| 2. Identity and permissions | Fictional users/roles, group IDs, source ACL principals, source ACL snapshot contracts, permission-drift evidence, and group-aware PostgreSQL RLS migration artifacts. | SSO-compatible auth, tenant context, real users, real groups, RBAC/ABAC, source ACL sync, Postgres RLS live tests, and permission drift alerts. |
| 3. Retrieval and citation quality | Deterministic lexical/vector scoring, local embedding boundary, SQL candidate path, reranker boundary, chunk-level citations, sentence-level evidence spans, citation span coverage metrics, and active-only source lifecycle filtering with a stale-source eval. | Production embedding/reranker provider, hybrid retrieval, metadata filters, query routing, recall@k, MRR/nDCG, context precision/recall, broader citation faithfulness, larger stale/conflict evals. |
| 4. Runtime durability | Local JSON default; partial Postgres path; local ingestion job ledger with retry/dead-letter semantics. | Connection pool, migrations, durable queue, transactional outbox, scheduled retry, crash recovery, backup/restore, and load/failure tests. |
| 5. Governed tool execution | Local deterministic tools and approval queue. | Real tool registry, scoped credentials, dry-run previews, approval owner/expiry/escalation, idempotent execution, compensation behavior, and connector outage handling. |
| 6. Observability and EvalOps | Local trace/audit, OTLP-like JSON export, trace-to-eval candidates, and shared export-boundary redaction for generated observability/eval-review artifacts. | OTel SDK spans, Phoenix/Langfuse/OpenAI trace backend, cost/latency/token/error metrics, reviewed trace-to-eval promotion, human labels, nightly regression, and failure clustering. |
| 7. Security and governance | Threat model, public safety scan, workflow security, model-gateway safety, deterministic controls, and `public_trace_export_redaction_v1` for trace export boundaries. | OWASP LLM Top 10 matrix, NIST AI RMF mapping, broader PII redaction, secret manager, retention/deletion controls, red-team cases, incident runbooks, and residual-risk language. |
| 8. Deployment and operator UX | Local-first demos, Docker/compose checks, separate UI surfaces. | Production-like stack with API, frontend, workers, Postgres/pgvector, queue, OTel collector, auth middleware, health/readiness, admin console, alerts, rollback, and runbooks. |

## Upgrade Strategy

Do not spread effort evenly across all three demos. That would make the
repository wide but shallow.

Best target narrative:

```text
Enterprise AI Control Plane
```

Product composition:

```text
Project 1 = production data spine
  source ingestion -> ACL sync -> hybrid retrieval -> citations -> evals -> traces

Project 2 = governed action layer
  proposed action -> dry-run preview -> approval -> idempotent execution -> audit

Project 3 = reliability layer
  traces + eval failures -> incident -> release block -> remediation -> regression
```

## Next Engineering Sequence

### 1. Build the Project 1 production data-plane slice

Goal:

```text
real document input -> parse -> chunk -> embed -> index -> retrieve -> cite -> eval
```

Work items:

- add file upload or local folder connector
- define parser output contract
- support at least Markdown/TXT/CSV/HTML first, then DOCX/PDF
- store source URI, title, section, page/span, content hash, version, tenant, ACL, and source lifecycle metadata
- run embedding/indexing as a job with retry/dead-letter behavior
- use Postgres/pgvector live path for at least one verified local flow
- add hybrid lexical/vector retrieval and reranker provider boundary
- verify chunk and sentence-level citation spans
- add evals for recall, context precision, abstention, permission leak, source lifecycle filtering, and conflicting source cases

Acceptance evidence:

- a document can be uploaded or synced and queried
- unauthorized users cannot retrieve or cite restricted chunks
- deleted or missing source documents disappear from retrieval
- citations point to parser-normalized chunk spans and answer-support sentence spans
- superseded sources remain auditable but are filtered from current retrieval and citation
- quality gate includes retrieval/citation/stale-source metrics

### 2. Make identity and permissions production-shaped

Goal:

```text
same corpus, different authenticated users, different permitted evidence
```

Work items:

- add a local auth middleware stub with tenant/user/group context
- persist tenants, users, groups, group memberships, and source ACLs
- test app-layer filters and Postgres RLS together
- add permission drift detection for source ACL changes
- record denied evidence counts without leaking restricted content

Acceptance evidence:

- two users asking the same query produce different evidence sets
- denied evidence is counted in traces/audit without content leakage
- RLS blocks direct unauthorized DB access in live checks

### 3. Replace local-only job semantics with durable runtime

Goal:

```text
ingestion and agent jobs survive retries, restarts, and partial failure
```

Work items:

- introduce a queue abstraction
- persist job state transitions transactionally
- add scheduled retry and backoff
- add outbox for side-effecting connector actions
- verify crash/restart recovery with deterministic tests

Acceptance evidence:

- failed ingestion can continue without duplicate chunks
- dead-letter records include safe summaries and replay instructions
- approval/tool execution cannot double-submit side effects

### 4. Add external observability and trace-to-eval loop

Goal:

```text
every important request is externally traceable and bad traces become evals
```

Work items:

- instrument API, retrieval, parser, embedding, model, tool, approval, audit, and eval spans
- emit OTel GenAI-compatible attributes where possible
- support one backend path: Phoenix, Langfuse, OpenAI traces, or OTel collector
- keep export-boundary redaction on every generated trace and trace-to-eval artifact
- add trace URL/ID to UI and API responses
- build trace-to-eval promotion with reviewer disposition and dataset version

Acceptance evidence:

- a UI trace ID maps to an external trace
- a bad trace can be promoted to a regression eval
- evaluation compares prompt/model/retrieval profile changes

### 5. Strengthen the first live read connector

Goal:

```text
GitHub issues/PRs behave like a real enterprise source, not just fixtures
```

Work items:

- add live smoke mode behind explicit env flags
- verify source cursor checkpoints
- map source permissions or repository visibility into ACL snapshots
- verify source deletion/prune against live API behavior
- expose connector health, lag, error, and retry state

Acceptance evidence:

- fixture mode remains deterministic for CI
- live mode is safe, opt-in, and redacts credentials
- source updates/deletions are reflected in retrieval and status

### 6. Add one governed write connector

Goal:

```text
the agent can propose a real action but cannot execute without governance
```

Choose one:

- GitHub issue comment
- Jira or Linear issue update
- CRM note draft
- email draft

Work items:

- scoped credential handling
- dry-run diff/preview
- approval owner and expiry
- idempotency key
- audit record
- rollback or compensation note

Acceptance evidence:

- unsafe direct execution is impossible
- approved execution is idempotent
- rejected action is visible to the user and recorded in audit

### 7. Create a unified operator console

Goal:

```text
one operational surface, not three disconnected demos
```

Surfaces:

- sources and sync health
- documents/chunks/citations
- permissions and denied evidence counts
- traces
- eval runs and failures
- approval queue
- release gates and incidents
- connector errors and dead letters

Acceptance evidence:

- a reviewer can diagnose an answer from source sync to retrieval to model to eval
- the UI shows current health without reading local files
- mobile and desktop screenshots remain stable

### 8. Add governance and deployment proof

Goal:

```text
the repo can explain how it would operate safely in production
```

Work items:

- OWASP LLM Top 10 control matrix
- NIST AI RMF mapping
- PII redaction before trace export
- retention and deletion policy
- incident runbook
- production-like compose stack
- health/readiness endpoints
- backup/restore and rollback checks
- load test envelope

Acceptance evidence:

- public docs state residual risk honestly
- safety controls have file owners and verification commands
- production-readiness claims are bounded by actual evidence

## Review Narrative

Use this framing:

```text
I built the production invariants first: permission before generation, grounded
citations, abstention, approval gates, audit, traces, evals, and release
blocking. I would not claim this is production software yet. The next industrial
step is to replace local fixtures with real ingestion, identity, Postgres/
pgvector, external observability, trace-to-eval operations, and governed
connectors while preserving those invariants.
```

Short version:

```text
This is not a toy chatbot. It is a production-minded AI control-plane reference.
The current value is in the invariants. The next work is turning the local
reference paths into durable production data, identity, runtime, observability,
and operations paths.
```

## Reference Links

- OpenAI production best practices: https://developers.openai.com/api/docs/guides/production-best-practices
- OpenAI evaluation best practices: https://developers.openai.com/api/docs/guides/evaluation-best-practices
- OpenAI trace grading: https://developers.openai.com/api/docs/guides/trace-grading
- OpenAI eval cookbook: https://developers.openai.com/cookbook/examples/evaluation/getting_started_with_openai_evals
- OpenAI business eval primer: https://openai.com/index/evals-drive-next-chapter-of-ai/
- OpenAI Agents SDK tracing: https://openai.github.io/openai-agents-python/tracing/
- OpenAI Agents SDK human-in-the-loop: https://openai.github.io/openai-agents-python/human_in_the_loop/
- OpenAI Agents SDK guardrails: https://openai.github.io/openai-agents-python/guardrails/
- Microsoft Azure RAG design guide: https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/rag/rag-solution-design-and-evaluation-guide
- AWS Generative AI Application Builder: https://docs.aws.amazon.com/solutions/latest/generative-ai-application-builder-on-aws/solution-overview.html
- AWS Well-Architected Generative AI Lens: https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/design-principles.html
- Dify: https://github.com/langgenius/dify
- Dify Enterprise: https://dify.ai/enterprise
- RAGFlow: https://github.com/infiniflow/ragflow
- FastGPT: https://fastgpt.io/
- MaxKB: https://github.com/1Panel-dev/MaxKB
- EnterpriseRAG-Bench: https://onyx.app/enterpriserag-bench
- Onyx RAG and Search: https://docs.onyx.app/overview/core_features/internal_search
- Onyx connectors and permission sync: https://docs.onyx.app/admin/connectors
- LangChain State of Agent Engineering 2026: https://www.langchain.com/state-of-agent-engineering
- LangSmith observability: https://info.langchain.com/AI-Observability
- Langfuse docs: https://langfuse.com/docs
- Phoenix docs: https://arize.com/docs/phoenix/
- LangGraph human-in-the-loop: https://docs.langchain.com/oss/python/langgraph/human-in-the-loop
- LangGraph persistence: https://docs.langchain.com/oss/python/langgraph/persistence
- OpenTelemetry GenAI semantic conventions: https://opentelemetry.io/docs/specs/semconv/gen-ai/
- OpenTelemetry GenAI spans: https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-spans/
- OWASP Top 10 for LLM Applications: https://owasp.org/www-project-top-10-for-large-language-model-applications
- OWASP Top 10 for Agentic Applications 2026: https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/
- NIST AI Risk Management Framework: https://doi.org/10.6028/NIST.AI.100-1
- Alibaba Bailian knowledge base limits: https://www.alibabacloud.com/help/zh/model-studio/rag-knowledge-base-specifications
- Alibaba Bailian permissions: https://www.alibabacloud.com/help/zh/doc-detail/2851098.html
- Baidu Qianfan AppBuilder: https://cloud.baidu.com/doc/APPBUILDER/s/1k765432
- Volcengine Coze professional overview: https://developer.volcengine.com/articles/7396885023502106636
