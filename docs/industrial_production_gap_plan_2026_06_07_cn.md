# Industrial Production Gap Plan - 2026-06-07

本文记录一次面向“真正工业可用”的外部横向扫描和本仓库差距判断。结论先行：

```text
当前项目已经是很强的 FDE / AI systems portfolio reference implementation。
它能证明候选人理解企业 AI 的权限、检索、引用、审批、审计、评测、发布闸门。
但它还不是可以直接接入真实企业身份、真实企业数据、真实业务工具并承担线上责任的生产系统。
```

最准确的对外说法：

```text
Production-minded reference implementation, not production software.
```

## Distance Judgment

| Target | Current maturity | Honest judgment |
| --- | ---: | --- |
| FDE portfolio / technical review artifact | 90%-93% | 已经非常强。能讲系统边界、风险控制、eval、trace、public repo hygiene、工业化取舍。 |
| Architecture review / take-home artifact | 84%-88% | 可信。Project 1/2/3 已经能形成 Enterprise AI Control Plane 叙事，但 reviewer 会继续追问真实 auth、真实 source API、durable worker、external observability。 |
| Controlled synthetic demo | 78%-84% | 很接近完整展示。可以稳定演示权限检索、引用、拒答、审批、审计、release gate，但仍是 local-first/synthetic-first。 |
| Low-risk internal pilot | 45%-55% | 还差一批硬工程：SSO/OIDC、durable Postgres/pgvector、queue/worker、真实 connector、外部 trace/eval、runbook、backup/restore。 |
| Sensitive enterprise production | 25%-35% | 仍然较远。需要租户隔离、源系统 ACL 同步、数据保留/删除、合规审计、负载/故障测试、事故响应、SRE ownership、部署和安全评审。 |

如果换成一句人话：

```text
它现在像一个很完整的工业系统“骨架和控制面证明”，不是一个已经长出真实企业肌肉、血管和运维团队的产品。
```

## External Industrial Baseline

这次横向扫描覆盖了生产 RAG、Agent、LLMOps、观测评测、安全治理和中国企业 AI 平台方向。公开资料里的共同模式很稳定：工业级不是“更会聊天”，而是围绕真实数据、真实身份、真实工具、真实失败和持续评测建立控制面。

| Source family | Public signal | What it means for this repo |
| --- | --- | --- |
| Dify | 公开定位为 production-ready agentic workflow builder，覆盖 RAG pipelines、agentic workflows、integrations、observability。 | 工业项目需要 workflow/app builder、知识库运营、模型/工具/发布管理和可部署平台，不只是一个聊天 demo。 |
| FastGPT | 公开强调 enterprise AI productivity engine、visual workflows、hybrid retrieval、debugging/auditing、SSO/RBAC、production-ready architecture、enterprise delivery。 | 中国企业场景会非常看重私有化、权限、业务系统集成、工作流交付、审计和客户现场可控性。 |
| Onyx | 文档强调 connectors 会索引组织应用中的 documents、metadata、permissions，并近实时保持更新；权限同步是企业能力。 | 企业 RAG 最难的不是问答本身，而是源系统连接、权限同步、删除/更新、用户级可见性。 |
| EnterpriseRAG-Bench | 约 50 万企业文档，覆盖 Slack、Gmail、Linear、Drive、HubSpot、Fireflies、GitHub、Jira、Confluence 等源和多类复杂问题。 | 当前 eval corpus 太小。下一跳可信度来自更大、更脏、更冲突、更接近企业的检索评测集。 |
| RAGFlow | 公开强调 deep document understanding、grounded citations、复杂文档解析、template chunking、multiple recall、reranking、self-hosting。 | Project 1 已有正确安全边界，但需要更强 parsing、page/span/table/OCR、多路召回、rerank 和 citation verification。 |
| LangGraph | durable execution 保存 workflow checkpoint，适合 human-in-the-loop、long-running tasks、checkpoint continuation，不重复 side effects。 | Project 2 的审批方向正确，但工业 agent 必须能进程重启后继续，且 side effects 需要幂等和 outbox。 |
| LangSmith | evaluation 分 offline/online；生产 trace 可自动跑 evaluator、monitor、alert，并把失败 trace 加回 dataset。 | 本仓库已有 local eval/trace，但还需要 trace -> human review -> dataset -> regression -> release gate 的真实闭环。 |
| Phoenix / Arize | Phoenix 是 open-source tracing/evaluation 工具，支持 OTel 接收、trace viewer、datasets、rerun/compare。 | 本仓库的 local JSON trace 需要升级为外部可观测平台可消费的 span、dataset 和 experiment。 |
| Langfuse / OpenLIT | 公开定位覆盖 tracing、metrics、evals、prompt management、datasets、OpenTelemetry 集成。 | 工业 LLMOps 不只看最终回答，要管理 prompt 版本、成本、latency、token、失败聚类和人工标注。 |
| OpenTelemetry GenAI conventions | 定义 GenAI span/event/metric/attribute，并提醒 prompt/output 可能很大且含敏感内容。 | trace 不能随便全量裸奔；要有 OTel 语义、redaction、sampling、token/cost/error metrics。 |
| Ragas | 指标覆盖 context precision/recall、faithfulness、response relevancy、noise sensitivity、tool call accuracy、agent goal accuracy。 | 当前 retrieval metrics gate 是正确方向，但要扩展到更大 corpus、噪声、冲突、缺失答案和 agent tool metrics。 |
| OpenAI Agents / Evals | 官方强调 agent traces、tool calls、handoffs、guardrails、trace grading、datasets、evals。 | 未来对 OpenAI FDE 方向，最重要的是会把 agent 行为做成可追踪、可评分、可回归的工程系统。 |
| OWASP LLM / Agentic risks | Prompt injection、sensitive information disclosure、excessive agency、insecure tool/output/vector risks 都是核心风险。 | 当前 threat model 很好，但要继续变成 OWASP/NIST 映射、控制 owner、测试、runbook 和 residual risk。 |
| NIST AI RMF / GenAI Profile | 强调在设计、开发、使用、评估、治理中系统性管理 AI 风险。 | 工业项目需要风险归属、监控、事故响应、数据治理、文档和发布责任，不只是技术演示。 |

## Current Strengths

| Area | Evidence in repo | Why it matters |
| --- | --- | --- |
| Security invariant | 权限过滤发生在生成前，模型不是安全边界；Project 2 侧效应需要审批。 | 这比普通 RAG/Agent demo 强很多，因为它把风险控制放在应用层。 |
| Project 1 data spine | admin ingestion、source sync、source bundle connector、GitHub read connector contract、job ledger、retry/dead-letter、source lifecycle、connector status。 | 已经开始像数据接入系统，而不是 seed fixture demo。 |
| Retrieval quality | deterministic embedding/reranker boundary、citation spans、active-only filter、retrieval metrics gate（recall@k、MRR、nDCG@k、ranked context precision、citation-context alignment、security-event coverage、permission-block、stale-source filtering）。 | 能证明检索质量和引用质量，不只是“最后答案看起来对”。 |
| Project 2 governance | approval queue、side-effect blocking、sanitized action outbox、retry/dead-letter states、local worker lease proof、action-run receipt、idempotent execution direction。 | 进入了企业 agent 的关键模式：AI 先提出动作，人/策略批准后再执行，并留下可审计的 dispatch checkpoint、派发失败证据、重试恢复证据和本地 worker ownership 证据。 |
| Project 3 reliability | eval failure -> incident evidence -> release block -> remediation/regression。 | 能讲清楚 AI app 发布不是改 prompt 后直接上线。 |
| Public maintainability | README、case study、API docs、threat model、CI、public safety scan、issue/PR policy、visual assets。 | 对 FDE 技术评审非常有价值，说明你不是只会写孤立 demo。 |

## Main Production Gap

最大的缺口不是 UI，也不是多接一个模型 API，而是：

```text
real enterprise data plane + identity plane + durable runtime plane + observability/eval plane + operations model
```

真正工业链路应该长这样：

```text
source system
  -> authenticated connector
  -> source ACL sync
  -> parser worker
  -> chunk/embed/index
  -> permission-aware retrieval
  -> cited answer or abstention
  -> trace/eval/alert
  -> operator recovery
```

当前仓库已经有这条链的骨架，但大部分环节仍然是 local-first、fixture-first、synthetic-first。

## Eight Gap Matrix

| Gap | Current state | Industrial target |
| --- | --- | --- |
| 1. Data ingestion/parsing | Seed/admin/source-bundle/GitHub read connector, job ledger, source lifecycle. | Real connectors, uploads, PDF/DOCX/table/OCR/image parsing, parser versioning, source spans, incremental sync, prune/delete verification. |
| 2. Identity/permissions | Local users/roles/groups/ACL snapshots, demo token boundary, Postgres RLS artifacts. | SSO/OIDC, real tenants/users/groups, source ACL sync, RBAC/ABAC, live RLS tests, permission drift alerting. |
| 3. Retrieval/citation quality | Local deterministic retrieval, reranker boundary, citations, metrics gate with recall@k, MRR, nDCG@k, ranked context precision, citation-context alignment, security-event coverage, permission blocking, and stale-source filtering. | Production embedding/reranker, hybrid retrieval profiles, metadata filters, query routing, larger-corpus context precision/recall, conflict/noise evals. |
| 4. Runtime durability | Local JSON default, optional Postgres path, inline job behavior, local action outbox checkpoint with retry/dead-letter and worker lease proof. | Durable Postgres/pgvector, queue/worker fleet, transactional outbox, crash recovery, backup/restore, load/failure tests. |
| 5. Governed tool execution | Approval queue, blocked direct side effects, sanitized action outbox, retry/dead-letter states, local worker lease evidence, action receipt direction. | Tool registry, scoped credentials, dry-run preview, approval owner/expiry/escalation, idempotent execution, connector-specific retry/dead-letter/compensation behavior. |
| 6. Observability/EvalOps | Local traces/audit/evals, OTLP-shaped export, trace-to-eval candidates, checked-in reviewed eval ledger, read-only nightly regression workflow. | OTel spans, Phoenix/Langfuse/OpenAI trace backend, dashboards, alerts, token/cost/latency/error metrics, human labels from real incidents, failure clustering. |
| 7. Security/governance | Threat model, safety scan, redaction, model gateway safety. | OWASP/NIST mapping, PII controls, secret manager, retention/deletion, red-team cases, incident runbooks, residual-risk register. |
| 8. Deployment/operator UX | Local apps, docs, screenshots, Docker checks. | Production-like stack: API, frontend, workers, Postgres/pgvector, queue, OTel collector, auth middleware, health/readiness, rollback, runbook. |

## Recommended Upgrade Shape

不要平均强化三个项目。最短路线是把三个项目统一成一个更强叙事：

```text
Enterprise AI Control Plane
```

职责分层：

```text
Project 1 = production data spine
  source ingestion -> ACL sync -> parser/chunk/embed/index -> retrieval -> citation -> eval/trace

Project 2 = governed action layer
  proposed action -> dry-run preview -> approval -> action outbox -> idempotent execution -> audit/action receipt

Project 3 = reliability layer
  traces/eval failures -> incident -> release block -> remediation -> regression
```

## Build Plan

### 1. Project 1: real data-plane slice

Goal:

```text
one real source -> parse -> chunk -> embed -> index -> retrieve -> cite -> eval -> trace
```

Work:

- Add one high-signal connector path first: GitHub repository content, local folder upload, or Drive-like source bundle.
- Add parser output contract: source_uri, content_hash, parser_version, page/section/span, mime_type, acl_snapshot, warning_count.
- Add parser worker mode with retry/dead-letter already visible in job ledger.
- Run live Postgres/pgvector path on Docker-enabled machine.
- Prove prune/delete: removed source cannot be retrieved or cited.
- Add noisy/conflicting/near-duplicate/absent-answer evals.

Acceptance:

- Allowed user can get cited evidence.
- Blocked user cannot retrieve restricted evidence.
- Deleted source disappears from retrieval and citation.
- Failed ingestion job can be retried or dead-lettered with audit evidence.

### 2. Project 1: identity and permission sync

Goal:

```text
same corpus, different authenticated users, different retrievable evidence
```

Work:

- Keep local signed token for demo, but add OIDC-compatible middleware contract.
- Separate tenant, user, group, role, source principal, source ACL.
- Add permission drift tests: ACL changes after ingestion.
- Add live RLS test against Postgres.

Acceptance:

- User A can cite a document.
- User B cannot retrieve it.
- Denied evidence count is auditable without leaking body/title/chunk content.

### 3. Project 2: durable governed actions

Goal:

```text
agent proposes -> preview -> approval -> persisted execution -> audit/outbox
```

Work:

- Add workflow checkpoint state or LangGraph-like persisted run model.
- Promote the current local action outbox into a transactional DB-backed outbox.
- Add idempotency keys per approval and tool execution.
- Add approval owner, expiry, escalation, rejection reason, compensation notes.
- Add scoped tool credentials and dry-run preview contract.
- Add retry/dead-letter state for failed dispatch, with operator-visible recovery notes.

Acceptance:

- Restarting the service does not lose pending approvals.
- Re-approving does not duplicate a side effect.
- Action receipt contains hashes/refs, not raw sensitive body.
- Audit trail can reconstruct who approved what and what happened after approval.
- A failed tool dispatch lands in retry/dead-letter state without losing approval context.

### 4. Project 3: trace-to-eval production loop

Goal:

```text
trace -> review -> eval candidate -> regression -> release decision
```

Work:

- Emit OTel-compatible spans for request, retrieval, model, tool, approval, audit, eval, release decision.
- Add optional Phoenix or Langfuse local backend path.
- Extend the checked-in reviewed eval ledger from local synthetic traces to real public-safe failure logs.
- Add failure clustering and reviewer label history.

Acceptance:

- A failed production-like run can be inspected outside the app.
- A reviewed failure becomes an eval case.
- A fix is blocked until the regression passes.

### 5. Deployment and operations

Goal:

```text
one-command production-like local stack
```

Work:

- Compose stack: API apps, frontend, Postgres/pgvector, queue, worker, OTel collector, observability backend.
- Add health/readiness endpoints and smoke flows.
- Add backup/restore drill for Postgres state.
- Add operator runbook for ingestion failure, permission mismatch, eval regression, tool outage, trace export failure.

Acceptance:

- Fresh machine can start the stack with documented commands.
- Runtime failure can be diagnosed from runbook + traces + audit.
- Public claim remains honest: production-shaped local stack, not enterprise production deployment.

## Review Positioning

Best answer:

```text
I built this as a production-minded reference system, not as a fake "production-ready" claim.
The important part is that the security and reliability boundaries are explicit:
permissions before generation, citations and abstention, approval before side effects,
audit/action receipts, eval gates, and trace-to-eval workflow.
The remaining work is not more prompting. It is real identity, real connectors,
durable workers, external observability, and operational ownership.
```

What not to say:

```text
This is already an enterprise production AI platform.
```

Better wording:

```text
This is the reference implementation I would use to discuss and then build the production version.
It shows the invariants I care about, and the roadmap identifies the exact hard parts left.
```

## Source Notes

Key public references checked in this pass:

- Dify: https://dify.ai/
- FastGPT: https://fastgpt.io/
- MaxKB: https://github.com/1Panel-dev/maxkb
- Onyx RAG/Search: https://docs.onyx.app/overview/core_features/internal_search
- Onyx connectors: https://docs.onyx.app/admin/connectors
- EnterpriseRAG-Bench: https://arxiv.org/abs/2605.05253
- Temporal durable execution: https://temporal.io/
- LangGraph durable execution: https://docs.langchain.com/oss/python/langgraph/durable-execution
- LangGraph human-in-the-loop interrupts: https://docs.langchain.com/oss/python/langgraph/human-in-the-loop
- LangSmith evaluation: https://docs.langchain.com/langsmith/evaluation
- LangSmith observability: https://docs.langchain.com/langsmith/observability-concepts
- Phoenix docs: https://arize.com/docs/phoenix
- Langfuse GitHub: https://github.com/langfuse/langfuse
- OpenLIT GitHub: https://github.com/openlit/openlit
- OpenTelemetry GenAI conventions: https://opentelemetry.io/docs/specs/semconv/gen-ai/
- Ragas metrics: https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/
- OpenAI Agents: https://platform.openai.com/docs/guides/agents
- OpenAI Agents SDK tracing: https://openai.github.io/openai-agents-js/guides/tracing/
- OpenAI Agents SDK guardrails: https://openai.github.io/openai-agents-js/guides/guardrails/
- OpenAI production best practices: https://platform.openai.com/docs/guides/production-best-practices
- OpenAI rate limits: https://platform.openai.com/docs/guides/rate-limits
- OpenAI Agent evals: https://platform.openai.com/docs/guides/agent-evals
- OpenAI trace grading: https://platform.openai.com/docs/guides/trace-grading
- OWASP LLM Top 10: https://owasp.org/www-project-top-10-for-large-language-model-applications
- NIST GenAI Profile: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf
