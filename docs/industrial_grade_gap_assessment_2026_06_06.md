# Industrial Grade Gap Assessment

Date reviewed: 2026-06-06

This note records a web-refreshed judgment on how far this repository is from a
genuinely production-usable industrial AI system. It is intentionally direct:
the repository is already strong as an FDE / AI systems portfolio, but it is not
yet industrial production software.

## Verdict

| Target | Current distance | Judgment |
| --- | --- | --- |
| FDE portfolio / technical review artifact | Close | The repo demonstrates the right production-minded boundaries: permission-aware RAG, citations, abstention, approvals, side-effect blocking, trace IDs, audit logs, eval gates, CI, and public repo hygiene. |
| Serious architecture review or take-home | Close to medium | The story is credible and now includes a GitHub read connector contract, but reviewers may ask for live source permissions and durable worker execution instead of deterministic fixture mode. |
| Controlled pilot on low-risk internal data | Medium to far | Needs real auth, durable Postgres/pgvector runtime, parser/indexing jobs, source permissions, external observability, deletion/prune handling, and broader live connectors. |
| Production over sensitive enterprise data | Far | Needs identity, tenant isolation, source ACL sync, online evals, security operations, cloud deployment, backups, incident runbooks, and an owner model. |

Most honest framing:

```text
This is a production-minded reference implementation. It proves the control
boundaries a real enterprise AI system needs, but the production data plane,
identity plane, runtime plane, observability backend, and operations model still
need to be built.
```

## Public Industrial Signals

The current industrial ecosystem converges on a few repeated patterns.

| Reference | Public signal | Lesson for this repo |
| --- | --- | --- |
| OpenAI agent guide | Agents combine model, tools, and instructions/guardrails; useful agent systems act across workflows rather than only chatting. | Project 2 has the right side-effect governance idea, but needs durable workflow state and real tool connectors. |
| OpenAI Responses / eval guidance | New agentic apps should use the modern Responses surface, and production LLM apps need evals because model behavior is variable. | The model gateway path should stay opt-in and structured, while evals should expand from deterministic smoke cases into retrieval and trace regression suites. |
| OpenAI rate-limit guidance | Production clients need backoff, token budgeting, org/project isolation, and usage-tier awareness. | The repo still needs provider retry, rate-limit, budget, and cost telemetry controls before real traffic. |
| Azure AI Search RAG guidance | Enterprise RAG must handle multi-source access, token constraints, response time expectations, security trimming, citations, and retrieval metadata. | Project 1 is aligned conceptually, but needs real source ingestion, security-trimmed retrieval at scale, and live hybrid search. |
| AWS Well-Architected Generative AI Lens | Mature GenAI systems are reviewed through security, reliability, operational excellence, performance, cost, sustainability, data architecture, and responsible AI. | The repo needs an operator and deployment plan, not only application-level controls. |
| OpenAI Agents SDK tracing | Production agent traces record model generations, tool calls, handoffs, guardrails, custom events, and sensitive-data controls. | Local traces are good; production needs real trace processors and privacy controls. |
| Dify | Public repo positions Dify as a production-ready agentic workflow platform with API, web, workflow, agent, Docker, E2E, SDK, and stress-test surfaces. | Industrial products expose an operator platform, not separate toy demos. |
| RAGFlow | Large deployable RAG engine with deep document understanding, agent/RAG modules, Docker/Helm, API, MCP, memory, and vector/search infrastructure. | Project 1 needs real parsing, embedding, hybrid retrieval, reranking, source spans, and ingestion operations. |
| Haystack | Production-ready LLM apps emphasize modular pipelines with explicit control over retrieval, ranking, filtering, memory, routing, tools, generation, and evaluation. | The repo should keep explicit boundaries instead of hiding logic behind prompts. |
| LangGraph | Production agent systems emphasize durable execution, human-in-the-loop, memory, observability, and deployment for long-running stateful agents. | Approval workflows should survive restarts and continue deterministically. |
| Langfuse | LLMOps platforms bundle traces, metrics, evals, prompt management, playgrounds, and datasets. | Static evals are not enough; traces should feed eval datasets and regression gates. |
| OpenTelemetry GenAI conventions | GenAI observability now has conventions for model spans, agent spans, metrics, events, and provider-specific attributes. | Use OTel spans for API, retrieval, model, tool, approval, audit, and eval events. |
| Phoenix / RAGAS | Open-source LLMOps and RAG evaluation tools emphasize traces, datasets, experiments, context precision/recall, and faithfulness. | Add a stable external evaluation/observability surface instead of relying only on local JSON traces. |
| Onyx / EnterpriseRAG-Bench | Enterprise RAG is tested on 500K+ documents, 500 questions, and 9 internal source types with permission-aware retrieval expectations. | The current fictional seed corpus is tiny; production credibility requires larger noisy corpora and source ACL sync. |
| OWASP LLM Top 10 / NIST AI RMF | Prompt injection, excessive agency, data leakage, vector weaknesses, and lifecycle risk governance are explicit industrial concerns. | The threat model should become a mapped security control matrix with tests, owners, and incident procedures. |

Source links reviewed:

- OpenAI agent guide: https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/
- OpenAI Responses API: https://platform.openai.com/docs/api-reference/responses/compact
- OpenAI migration guidance: https://platform.openai.com/docs/guides/migrate-to-responses
- OpenAI eval best practices: https://platform.openai.com/docs/guides/evaluation-best-practices
- OpenAI rate-limit best practices: https://help.openai.com/en/articles/6891753
- Azure AI Search RAG overview: https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview
- Azure Search OpenAI Demo: https://github.com/Azure-Samples/azure-search-openai-demo
- AWS Well-Architected Generative AI Lens: https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/generative-ai-lens.html
- OpenAI Agents SDK tracing: https://openai.github.io/openai-agents-python/tracing/
- Dify: https://github.com/langgenius/dify
- RAGFlow: https://github.com/infiniflow/ragflow
- Haystack: https://github.com/deepset-ai/haystack
- LangGraph: https://github.com/langchain-ai/langgraph
- Langfuse: https://github.com/langfuse/langfuse
- OpenTelemetry GenAI conventions: https://opentelemetry.io/docs/specs/semconv/gen-ai/
- Phoenix: https://arize.com/docs/phoenix/
- RAGAS metrics: https://docs.ragas.io/en/latest/concepts/metrics/available_metrics/
- Onyx EnterpriseRAG-Bench: https://onyx.app/enterpriserag-bench
- Onyx connector permissions: https://docs.onyx.app/admin/connectors
- Qdrant hybrid search with reranking: https://qdrant.tech/documentation/tutorials-search-engineering/reranking-hybrid-search/
- OWASP LLM Top 10: https://owasp.org/www-project-top-10-for-large-language-model-applications/
- NIST AI RMF: https://doi.org/10.6028/NIST.AI.100-1
- NIST Generative AI Profile: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf

## What The Repo Already Has

| Area | Current strength |
| --- | --- |
| Security boundary | The model is not the security boundary. Permissions and side effects are enforced in application code. |
| RAG controls | Project 1 demonstrates role-filtered evidence, citations, abstention, admin ingestion, prompt-injection handling, traces, audit logs, and evals. |
| Agent controls | Project 2 blocks direct side effects, creates approvals, requires supervisor execution, and records audit evidence. |
| Release reliability | Project 3 links failed eval evidence to blocked rollout decisions. |
| Deterministic evals | Golden evals catch unsafe leaks, unsupported answers, unsafe side effects, and unsafe release approvals. |
| Public hygiene | README, docs, screenshots, CI, release assets, GitHub governance, and contributor policy are unusually complete for a portfolio repo. |
| Production direction | Postgres/pgvector schema, RLS policies, migration checks, seed SQL, repository interfaces, and optional model gateways show a clear upgrade path. |

## Main Production Gaps

| Gap | Current state | Industrial requirement |
| --- | --- | --- |
| Real ingestion | Fictional seed data plus local/admin ingestion, connector-style source sync, ingestion jobs, and a GitHub issue/PR read connector contract. | Uploads, broader source connectors, parser jobs, OCR/table handling, incremental sync, deletion/prune handling, backfills, source versions, and failed-job recovery. |
| Retrieval quality | Deterministic lexical/vector scoring now has a local embedding boundary, optional PostgreSQL SQL keyword/vector candidate selection, and a local reranker boundary, but it is still small-corpus and not production-provider backed. | Production embedding provider, larger hybrid retrieval metrics, production reranker, query routing, metadata filters, recall@k, citation faithfulness, and stale-source tests. |
| Source permissions | UI-selected fictional users and roles plus a connector ACL snapshot contract with permission-drift evidence. | Enterprise SSO, tenant model, group membership, RBAC/ABAC, real source ACL sync, RLS defense in depth, live permission-drift detection. |
| Runtime durability | Local JSON remains the safe default; Postgres path is partial; Project 1 now has a local ingestion job ledger with idempotency, dead-letter, retry parent, and audit evidence. | Connection pooling, migrations, transactional audit, real queue backend, scheduled retries, outbox, crash recovery. |
| Agent workflow | Local deterministic tools and approval model. | Real tool registry, scoped credentials, preview diffs, approval ownership/expiry/escalation, idempotent execution, connector outage handling. |
| Observability | Local trace IDs and OTLP-shaped export. | OpenTelemetry SDK, Phoenix/Langfuse/OpenAI traces, dashboards, production trace sampling, cost/latency/error metrics. |
| Eval operations | Static deterministic golden cases. | Trace-to-eval promotion, human annotation, nightly regression, online evals, model/prompt comparison, failure clustering. |
| Security governance | Good threat model and public hygiene. | OWASP-mapped test suite, PII redaction, secret manager, data retention/deletion, audit retention, red-team runbooks. |
| Deployment | Local-first Python demos and Docker files. | Cloud IaC, API gateway, auth middleware, managed DB/search, worker fleet, OTel collector, backups, rollbacks, load tests. |
| Operator UX | Three separate demo UIs. | Unified admin surface for sources, permissions, sync health, evals, traces, approvals, incidents, and release gates. |

## Recommended Direction

Do not industrialize all three demos equally. That would make the repo wide but
shallow.

Best product direction:

```text
Project 1 becomes the production spine:
  source ingestion -> permission sync -> hybrid RAG -> citations -> evals -> traces.

Project 2 becomes the governed action layer:
  retrieved context -> proposed tool action -> dry-run preview -> approval -> idempotent execution.

Project 3 becomes the reliability layer:
  traces + eval failures -> incidents -> release blocking -> remediation -> regression tests.
```

Target system:

```text
Enterprise AI Control Plane

sources + ACL sync
  -> parser / chunk / embed / index jobs
  -> permission-aware hybrid retrieval
  -> citation-grounded answers
  -> governed agent actions
  -> approval queue
  -> trace + audit + eval loop
  -> release gate and incident console
```

## Concrete Upgrade Plan

### 1. Finish The Production Data Plane Slice

Implement and verify one end-to-end Project 1 path:

- file upload or local connector
- parser output contract
- chunk metadata with source URI, title, section/page/span, version, hash, tenant, ACL
- embedding generation
- pgvector storage
- BM25/full-text path
- hybrid fusion
- reranker hook
- permission filter before answer assembly
- citation spans
- retrieval evals

Success criteria:

- Upload or sync a document.
- Ask a question.
- Retrieve the correct chunk.
- Cite it.
- Abstain when evidence or permission is missing.
- Pass permission-leak, recall@k, citation, and stale-source evals.

### 2. Make Identity And Permissions Real Enough

Build a local enterprise-auth stub before full SSO:

- tenant table
- users
- groups
- memberships
- source ACL fixtures
- role policy
- department policy
- RLS-backed tests
- permission drift evals. Current API contracts cover a local ACL snapshot drift case; the remaining gap is live user/group sync and RLS-backed proof.

Success criteria:

- Two users with different source ACLs see different retrieval results from the same corpus.
- Unauthorized relevant evidence is counted for observability but never leaked to the answer layer.

### 3. Add External Observability

Instrument live requests:

- API span
- retrieval span
- parser span
- embedding span
- model span
- tool span
- approval span
- audit span
- eval span

Send them to one backend:

- Phoenix, Langfuse, OpenAI traces, or another OTel-compatible collector.

Success criteria:

- A UI trace ID maps to a backend trace.
- A bad trace can be converted into an eval case.
- Cost, latency, model, prompt version, retrieval profile, and tool decisions are visible.

### 4. Extend The First Real Connector

The repository now has a GitHub read connector boundary with deterministic fixture mode and a live REST adapter path. Extend it before adding many new connectors:

- source user/group permission sync
- deletion/prune detection
- durable cursor checkpoints
- connector health and backfill logs
- retry scheduling through a real worker queue
- live smoke proof in an authenticated environment

Then add one governed write connector:

- GitHub issue comment, Jira/Linear update, CRM note draft, or email draft.

Success criteria:

- Connector credentials are scoped.
- Sync state is durable.
- Permission sync is represented.
- Write action requires dry-run preview, approval, idempotency key, and audit.

### 5. Turn Evals Into An Operations Loop

Add:

- larger enterprise-style corpus fixture
- expected source chunk IDs
- recall@k
- MRR or nDCG
- citation coverage
- answer faithfulness
- abstention correctness
- permission-leak tests
- stale/conflicting-info tests
- trace-to-eval promotion
- model/prompt/retrieval experiment comparison

Success criteria:

- A retrieval or prompt change cannot merge if it regresses safety or key retrieval metrics.
- A production-like failure becomes a permanent regression test.

### 6. Security And Deployment Hardening

Add:

- OWASP LLM Top 10 control matrix
- prompt-injection and indirect-injection red-team pack
- PII detection/redaction before model calls and trace export
- secrets manager pattern
- data retention and deletion workflows
- backup/restore docs
- health/readiness endpoints
- cloud deployment reference
- rollback and incident runbooks

Success criteria:

- A reviewer can map each major risk to code, tests, logs, and an operational owner.
- A clean environment can be deployed, smoke-tested, monitored, and rolled back.

## Priority Ranking

Highest leverage:

1. Project 1 parser/chunk/embed/pgvector/hybrid retrieval/citation/eval slice.
2. Source ACL sync plus RLS-backed permission tests.
3. OTel trace export into Phoenix/Langfuse/OpenAI traces.
4. Trace-to-eval promotion and model/prompt comparison.
5. Harden the GitHub read connector, then add one governed write connector.
6. Unified operator console for sources, evals, traces, approvals, and release gates.
7. OWASP/NIST control matrix and deployment runbooks.

## Technical Review Framing

Use this:

```text
I would not claim this is production software yet. I built it as a
production-minded reference implementation. The important part is that the
invariants are already in application code: permissions before generation,
citations and abstention, side-effect approval, trace/audit evidence, and eval
release gates. To make it industrial, I would replace the local state and seed
data with authenticated multi-tenant Postgres/pgvector, real ingestion and
source ACL sync, hybrid retrieval with reranking, OpenTelemetry traces feeding
an eval loop, and a governed connector runtime with idempotent approvals.
```

## Bottom Line

The repo is already above normal portfolio quality. It is probably good enough
to support an FDE-style technical conversation because it demonstrates the right
system instincts.

It is still not production-ready. The gap is not "make the model smarter"; the
gap is building the industrial substrate around the model: data ingestion,
identity, permissions, durable runtime, observability, eval operations,
security governance, deployment, and support ownership.
