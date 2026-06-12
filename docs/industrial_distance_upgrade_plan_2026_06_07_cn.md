# Industrial Distance And Upgrade Plan - 2026-06-07

本文记录一次严格的外部扫描和本仓库差距判断。结论先行：

```text
这个仓库已经是很强的 FDE / AI systems reference implementation。
它能证明很多正确的企业 AI 控制边界。
它距离真正承载敏感企业数据的工业系统，仍然有一段明显距离。
```

最准确的对外定位：

```text
Production-minded reference implementation.
```

不要把它包装成已经可以直接接入真实客户数据、真实身份系统、真实业务系统并承担线上责任的产品。

## Current Distance

| Target | Distance | Current maturity | Judgment |
| --- | --- | ---: | --- |
| Public technical artifact | close | 88%-92% | 已经能讲清楚权限、RAG、citation、abstention、approval、trace、audit、eval、release gate。 |
| Serious architecture review artifact | close to medium | 80%-86% | 架构方向可信，且已经有 connector、source bundle、job ledger、Postgres/pgvector path、retrieval metrics gate。 |
| Controlled synthetic demo | close | 70%-78% | 本地 demo 和 CI 很完整，可以稳定展示生产不变量，但仍是 synthetic/local-first。 |
| Low-risk internal pilot | medium to far | 42%-52% | 需要真实 auth、durable DB/queue/worker、真实 connector、external observability、operator runbook。 |
| Sensitive enterprise production | far | 25%-35% | 需要 SSO/OIDC、tenant isolation、source ACL sync、backup/restore、load/failure tests、security/compliance/incident ownership。 |

一句话判断：

```text
差的不是一个 UI 页面，也不是再接一个模型 API。
真正缺的是 industrial data plane + identity plane + runtime plane + observability plane + operations model。
```

## What Industrial Projects Actually Have

外部扫描覆盖了 Dify、RAGFlow、FastGPT、Baidu Qianfan AppBuilder、Tencent Cloud ADP、Langfuse、Phoenix、Ragas、OpenTelemetry GenAI conventions、LangGraph、OpenAI Agents SDK、NVIDIA NeMo Guardrails、Unstructured/Docling/MarkItDown 等资料。

共同模式很清楚：工业系统不是“更会聊天”，而是围绕真实数据、真实身份、真实工具、真实失败和持续评测建立控制面。

| External signal | What it implies |
| --- | --- |
| Dify combines workflow, RAG pipeline, agent capability, model management, observability, APIs, Docker Compose, Grafana, Kubernetes and cloud deployment references. | 真正平台需要 app builder、operator surface、model/provider management、observability、deployment path，而不是单一 demo。 |
| RAGFlow emphasizes deep document understanding, template chunking, grounded citations, heterogeneous sources, multiple recall, reranking, self-hosting, Docling/MinerU, multimodal document handling, source sync, memory, MCP, and agentic workflow. | 工业 RAG 的核心难点在 messy documents、source sync、chunk/citation explainability、retrieval quality、deployment resources。 |
| FastGPT and Chinese enterprise platforms emphasize knowledge base, visual workflow, team/admin features, SSO/member sync, business process orchestration, application publishing, monitoring, and continuous optimization. | 中国企业落地更看重私有化、业务流程接入、知识库运营、权限空间、评测和持续调优。 |
| Langfuse and Phoenix treat tracing, prompt versioning, evals, datasets, experiments, human labels, cost/latency monitoring, and OTel compatibility as one loop. | 本项目已有 local trace/eval，但要进化成 trace -> label/review -> dataset -> regression -> release decision 的可运营链路。 |
| Ragas exposes RAG metrics such as context precision, context recall, response relevancy, faithfulness, noise sensitivity, and agent/tool metrics. | 当前 retrieval metrics gate 是正确方向，但 corpus 还太小，指标还要覆盖更大、更脏、更冲突的企业语料。 |
| OpenTelemetry GenAI conventions define GenAI spans and token/model attributes, while warning that prompt/output fields can contain sensitive data. | trace 不能只是本地 JSON；要有 OTel-compatible spans、redaction、sampling、token/cost/error metrics。 |
| LangGraph persistence saves graph state as checkpoints for human-in-the-loop, memory, time travel debugging, and fault-tolerant execution. | Project 2 的 approval 概念正确，但需要 restart-safe workflow checkpoints。 |
| OpenAI Agents SDK tracing records generations, tool calls, handoffs, guardrails, and custom events. | Agent 系统要能解释每一步，尤其是工具调用、handoff、guardrail trip、approval decision。 |
| NVIDIA NeMo Guardrails separates input, retrieval, dialog, execution, and output rails. | 安全控制不能只在 prompt；检索、工具、输出都要分层控制。 |
| Unstructured says open-source parsing is a starting point and production scenarios should use stronger pipeline/API paths. | 文档解析是工业 RAG 大坑；PDF/DOCX/table/OCR/multimodal parsing 不能靠简单文本切块糊过去。 |

## Current Strengths

| Area | Current evidence in this repo | Why it matters |
| --- | --- | --- |
| Security invariant | Permission filtering happens before generation; unsafe side effects need deterministic approval gates. | 这比普通 RAG demo 强很多，因为模型不是安全边界。 |
| Project 1 data spine | Admin ingestion, source sync, source bundle connector, GitHub read connector, ingestion jobs, idempotency, retry parent, dead letter, connector status, opt-in prune. | 已经不是单纯 seed data；开始接近工业数据接入边界。 |
| Retrieval and citation | Hybrid local scoring, deterministic embedding boundary, reranker boundary, citation spans, source lifecycle filtering, retrieval metrics gate with recall@k, MRR, nDCG@k, ranked context precision, citation-context alignment, security-event coverage, permission blocking, and stale-source filtering. | 已经开始能证明 retrieval quality，而不是只看最终回答。 |
| Project 2 governed actions | Tool side effects are blocked unless supervisor approval occurs; side-effect tools now expose registry policy, dry-run previews, owner/expiry metadata, rejection/expiry terminal states, sanitized action-outbox records, retry/dead-letter states, and local worker lease evidence. | 符合企业里“AI 提议，人/系统按策略执行”的模式，并且能解释审批前 dry-run、拒绝/过期、失败派发、重试恢复和当前本地 worker 证据边界。 |
| Project 3 reliability layer | Eval failure can block unsafe release and create incident evidence. | 有 AI app release gate 叙事，不是随便改 prompt。 |
| Public maintainability | README, case studies, API docs, threat model, safety scan, CI, issue/PR docs, release evidence. | 公开仓库已经像一个可审查工程资产。 |

## The Main Gap

最大短板是：

```text
还没有一条可长期运行的真实工业数据链。
```

目标链应该是：

```text
real source
  -> authenticated connector
  -> source ACL sync
  -> parser worker
  -> chunk/embed/index
  -> permission-aware retrieval
  -> cited answer
  -> trace/eval/alert
  -> operator recovery
```

当前项目已经有这条链的骨架，但多数环节仍是 local-first、fixture-first、synthetic-first。

## Eight Industrial Gaps

| Gap | Current state | Industrial target |
| --- | --- | --- |
| 1. Data ingestion and parsing | Text/file-like ingestion, source sync, source bundle, GitHub read connector. | Real connectors, multipart uploads, PDF/DOCX/table/OCR/image parsing, source versioning, backfill, delete/prune verification. |
| 2. Identity and permissions | Fictional users, roles, groups, ACL snapshots, local token boundary, Postgres RLS artifacts. | SSO/OIDC, real tenants/users/groups, source ACL sync, RBAC/ABAC, live RLS tests, permission drift alerting. |
| 3. Retrieval quality | Deterministic local embedding/reranker, citation spans, stale-source filter, retrieval metrics gate covering recall@k, MRR, nDCG@k, ranked context precision, citation-context alignment, security-event coverage, permission blocking, and stale-source filtering. | Production embedding/reranker, hybrid retrieval profiles, metadata filters, query routing, larger corpus context precision/recall, conflict/noise evals. |
| 4. Runtime durability | Local JSON default, optional Postgres path, local inline job contract, local action-outbox retry/dead-letter and worker lease proof. | Durable Postgres/pgvector, queue, worker fleet, transactional outbox, scheduled retry, backup/restore, load/failure tests. |
| 5. Governed tools | Local deterministic tool actions, tool registry, scoped credential labels, dry-run previews, approval queue, owner/expiry metadata, rejection/expiry states, sanitized action-outbox checkpoints, action-run receipts, and lease-backed retry evidence. | Policy-as-code registry, real scoped credentials, escalation routing, idempotent execution against external systems, compensation behavior, and production audit export. |
| 6. Observability and EvalOps | Local traces, audit, OTLP-shaped export, trace-to-eval candidates, checked-in reviewed eval ledger, and read-only nightly regression workflow. | OTel spans, Phoenix/Langfuse backend, dashboards, alerts, token/cost/latency/error metrics, reviewed trace promotion from real production failures, failure clustering. |
| 7. Security and governance | Threat model, public safety scan, model gateway safety, redaction policy. | OWASP/NIST mapping, broader PII controls, secret manager, retention/deletion, red-team cases, incident runbooks, residual-risk tracking. |
| 8. Deployment and operator UX | Local demos and static docs; separate UI surfaces. | Production-like compose/k8s stack, auth middleware, admin console, source health, permission audit, eval dashboard, approval queue, release/incident status. |

## Upgrade Strategy

不要平均强化三个项目。最短路线是把整个仓库升级成一个统一叙事：

```text
Enterprise AI Control Plane
```

三层职责：

```text
Project 1 = production data spine
  source ingestion -> ACL sync -> retrieval -> citations -> evals -> traces

Project 2 = governed action layer
  proposed action -> dry-run -> approval -> action outbox -> worker lease -> idempotent execution -> audit

Project 3 = reliability layer
  traces/eval failures -> incident -> release block -> remediation -> regression
```

## Priority Plan

### P0: Finish the current retrieval-quality slice

Keep the new Project 1 retrieval metrics gate as the current immediate checkpoint:

- required retrieval recall@k
- mean reciprocal rank
- required citation coverage
- permission-block coverage
- forbidden retrieval leak count
- stale-source filter coverage

Acceptance:

- The gate is part of `quality`.
- The demo report shows these metrics.
- Public docs explain that this is a checked-in local slice, not a large enterprise benchmark.

### P1: Build one real production data-plane slice

Goal:

```text
source -> parse -> chunk -> embed -> index -> retrieve -> cite -> eval
```

Work:

- Add a local folder or authenticated GitHub/Drive-like source connector path.
- Add parser output contract with file type, page/section/span, content hash, parser version, source URI, ACL metadata.
- Add worker-style ingestion with retry/dead-letter already visible in job ledger.
- Run at least one live Postgres/pgvector path on a Docker-enabled machine.
- Add delete/prune proof: removed source can no longer appear in retrieval or citation.
- Add noisy/conflicting source evals.

Acceptance:

- Admin syncs a source.
- Allowed user gets cited answer.
- Blocked user gets no leaked evidence.
- Deleted/pruned source disappears from current retrieval.
- Failed job is recoverable and auditable.

### P2: Make identity and permission sync credible

Goal:

```text
same corpus, different authenticated users, different retrievable evidence
```

Work:

- Keep local signed token for demo, then add OIDC-compatible middleware contract.
- Model tenant, user, group, role, source ACL, and source principal separately.
- Add permission drift cases: source ACL changes after ingestion.
- Add live RLS test against Postgres.

Acceptance:

- One user can cite a document.
- Another user cannot retrieve it.
- Denied evidence count is auditable without leaking body/title/chunk IDs.

### P3: External observability and trace-to-eval loop

Goal:

```text
trace -> review -> eval candidate -> regression -> release decision
```

Work:

- Emit OTel-compatible spans for API, ingestion, retrieval, model, tool, approval, audit, eval.
- Send traces to Phoenix or Langfuse in an opt-in local setup.
- Add cost/token/latency/error dashboards or documented exports.
- Add reviewed dataset ledger for promoted trace failures.

Acceptance:

- A failed run can be inspected outside the app.
- A reviewed trace becomes an eval case.
- Release gate blocks on the new regression.

### P4: Project 2 durable governed action

Goal:

```text
agent proposes -> preview -> approval -> persisted execution -> audit
```

Work:

- Add workflow checkpoint state.
- Add approval owner, expiry, escalation.
- Add tool registry with risk tier, dry-run schema, scopes, idempotency key.
- Add one safe write connector mock-live path, such as issue/comment/ticket update.

Acceptance:

- Service restart does not lose pending approval.
- Duplicate approval/execution does not duplicate side effects.
- Failed execution records recovery path.

### P5: Operator console and deployment hardening

Goal:

```text
an operator can understand health, risk, quality, and release state
```

Work:

- Unified operator surface for sources, connector status, jobs, ACL drift, retrieval metrics, traces, approvals, release gates.
- Production-like compose stack: API, frontend, worker, Postgres/pgvector, queue, OTel collector.
- Backup/restore and incident runbook.
- Retention/deletion workflow.

Acceptance:

- Fresh environment can start the full stack.
- Health/readiness endpoints separate service health from AI quality.
- Operator can answer: what broke, who is affected, what evidence supports the answer, what release is blocked.

## What I Would Say If Asked Whether It Is Industrial Today

```text
Not yet. The important application invariants are already explicit:
permission before generation, grounded citations, abstention, approval-gated
side effects, trace/audit evidence, and eval gates.

To make it truly industrial, I would preserve those invariants and replace
the local runtime with SSO/OIDC, Postgres/pgvector, durable workers, real
source connectors, OTel-backed observability, larger retrieval evals,
operator runbooks, and deployment/incident ownership.
```

## Source Notes

- Dify: https://github.com/langgenius/dify
- Dify Knowledge docs: https://docs.dify.ai/en/use-dify/knowledge/readme
- RAGFlow: https://github.com/infiniflow/ragflow
- FastGPT docs: https://doc.fastgpt.io/en/guide/getting-started
- Baidu Qianfan AppBuilder docs: https://cloud.baidu.com/doc/APPBUILDER/index.html
- Tencent Cloud ADP flow docs: https://cloud.tencent.com/document/product/1759/126433
- Langfuse docs: https://langfuse.com/docs
- Arize Phoenix docs: https://arize.com/docs/phoenix
- Ragas metrics: https://docs.ragas.io/en/latest/concepts/metrics/available_metrics/
- OpenTelemetry GenAI spans: https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-spans/
- LangGraph persistence: https://docs.langchain.com/oss/python/langgraph/persistence
- OpenAI Agents SDK tracing: https://openai.github.io/openai-agents-python/tracing/
- NVIDIA NeMo Guardrail types: https://docs.nvidia.com/nemo/guardrails/latest/about/rail-types.html
- Unstructured open-source overview: https://docs.unstructured.io/open-source/introduction/overview
- Docling: https://www.docling.ai/
- Microsoft MarkItDown: https://github.com/microsoft/markitdown
