# 工业真实可用差距与升级方案

Date: 2026-06-07

## 结论

当前仓库最准确的定位是：

```text
production-minded reference implementation, not production software
```

它已经能证明企业 AI 系统里最重要的一组控制不变量：

- 生成前做权限过滤，而不是让模型自己决定能不能看证据。
- 回答必须有引用；没有证据或无权限时拒答。
- 检索结果、引用、拒答、注入拦截、审批、工具执行、发布阻断都有 trace/audit/eval 证据。
- Agent 的副作用动作必须先进入审批和 action outbox，而不是由模型直接执行。
- 失败 trace 可以进入 review-only eval candidate，再由人审后进入回归集。
- 公开仓库有安全扫描、质量门、API 合同、UI 合同、威胁模型和治理控制映射。

但它还不能被诚实地称为“真正工业生产可用”。缺的不是再写一个更聪明的 prompt，而是：

```text
真实数据平面 + 真实身份权限平面 + 持久运行平面 + 外部可观测/评测平面 + 运维责任模型
```

## 当前验证快照

本地质量门已通过：

```text
python -B scripts/dev.py quality
```

关键结果：

- Project 1 eval: 14/14 passed
- Project 2 eval: 8/8 passed
- Project 3 eval: 6/6 passed
- Total evals: 28/28 passed
- Smoke tests: 13/13 passed
- API contracts: 150/150 passed
- Runtime UI contracts: 427/427 passed
- Observability integrity: 79/79 passed
- Trace-to-eval checks: 14/14 passed
- Reviewed eval ledger: 32/32 passed
- Threat model: 13 threats mapped
- Governance controls: 10 controls mapped to OWASP LLM Top 10, NIST AI RMF, and local threats

## 外部工业基线

这次主要对照了生产 RAG、Agent、LLMOps、可观测性、安全治理和中国企业 AI 平台方向。

| Source | 公开信号 | 对本仓库的含义 |
| --- | --- | --- |
| OpenAI eval guidance | Evals 是结构化测试，用来衡量 AI 系统在准确性、性能、可靠性上的表现；仅看单次输出不够。 | 继续把 eval 做成发布门，下一步要加线上 trace 回灌、人工标注和更大数据集。 |
| OpenAI Agents tracing | Agent trace 应覆盖 LLM generation、tool call、handoff、guardrail、自定义事件，并用于开发和生产监控。 | 当前本地 trace 方向正确，但要升级到 OTel/外部平台可消费的 span 和 dashboard。 |
| OpenAI prompt-injection guidance | Agent 系统要默认存在 prompt injection 和 exfiltration 风险，不能只靠输入分类器。 | 当前“模型不是安全边界”的设计是对的，下一步要强化工具权限、DLP、数据出站审批。 |
| Dify | 对外定位为 production-ready agentic workflow builder，覆盖 workflow、RAG、integration、observability。 | 工业产品需要工作流、知识库、工具集成、团队管理、发布管理，不只是聊天页面。 |
| FastGPT | 强调企业级 AI Agent、visual workflow、hybrid retrieval、debugging/auditing、私有化和企业交付。 | 中国企业场景会重点看私有部署、业务系统集成、审计、权限、现场可控性。 |
| MaxKB | 企业 AI assistant，包含 RAG pipeline、workflow、MCP tool-use。 | 国内企业平台趋势是“知识库 + 工作流 + 工具调用 + 多模型/私有模型”。 |
| RAGFlow | 强调 deep document understanding、复杂格式解析、引用、海量 token 检索。 | Project 1 要继续补 PDF/DOCX/table/OCR、source span、多路召回、rerank 和引用验证。 |
| LangGraph | persistence/checkpoint 用于 HITL、记忆、time travel、fault tolerance；生产中用持久 store。 | Project 2 的审批方向对，但还需要更像 durable workflow 的 checkpoint/continuation/crash recovery。 |
| Langfuse / Phoenix | LLM 工程平台强调 tracing、prompt management、evaluation、datasets、cost/latency。 | 当前 trace/eval 需要接外部观测平台，记录 token、成本、延迟、错误、实验版本。 |
| Ragas | RAG 指标覆盖 context precision/recall、noise sensitivity、faithfulness，Agent 指标覆盖 tool accuracy/goal accuracy。 | 当前 retrieval metrics 很好，但评测集太小，要上 noisy/conflicting/absent-answer 和 tool metrics。 |
| OWASP LLM Top 10 | 核心风险包括 prompt injection、sensitive information disclosure、supply chain、excessive agency、vector/embedding weaknesses 等。 | 治理 registry 要继续变成可测试、可审计、可追责的控制清单。 |
| NIST AI RMF / GenAI Profile | 生成式 AI 风险管理要覆盖 govern、map、measure、manage。 | 需要 owner、residual risk、incident response、retention/deletion、monitoring、release accountability。 |

## 距离估计

| 目标 | 当前成熟度 | 判断 |
| --- | ---: | --- |
| 技术展示/架构审查参考实现 | 90%-93% | 很强。能讲清楚企业 AI 控制面、质量门、安全边界和升级路线。 |
| 受控本地 demo | 80%-85% | 强。可以稳定演示权限 RAG、引用、拒答、审批、审计、trace、eval、release gate。 |
| 低风险内部试点 | 45%-55% | 还不够。需要真实身份、真实连接器、持久数据库、队列/worker、外部观测、runbook。 |
| 敏感企业生产 | 25%-35% | 距离明显。需要租户隔离、源系统 ACL 同步、DLP/PII、备份恢复、负载故障测试、合规和 SRE ownership。 |

一句话判断：

```text
现在是一个很完整的工业系统骨架和控制面证明，不是已经能接真实企业数据和真实业务责任的产品。
```

## 最高优先级升级路线

### 1. Project 1 做出一个真实数据平面切片

目标链路：

```text
source -> parse -> chunk -> embed -> index -> retrieve -> cite -> eval -> trace
```

要补：

- 一个真实连接器路径：GitHub repo content、local folder source、Drive-like bundle 三选一先做深。
- Parser contract：source URI、MIME、content hash、parser version、page/section/span、ACL snapshot、warnings。
- Worker 化 ingestion：retry、dead-letter、operator recovery。
- Postgres/pgvector 真实路径：不是只靠 JSON state。
- Prune/delete 证明：删除或失效 source 后不能再被检索或引用。
- 大一点的 eval corpus：噪声、冲突、近重复、过期、无答案、权限边界。

### 2. Project 1 补真实身份和权限同步模型

目标：

```text
same corpus, different authenticated users, different retrievable evidence
```

要补：

- OIDC-compatible middleware contract。
- tenant、user、group、role、source principal、source ACL 分离。
- source ACL 变更后的 permission drift test。
- Postgres RLS live test。

### 3. Project 2 补 durable governed action runtime

目标：

```text
agent proposes -> dry-run preview -> approval -> transactional outbox -> idempotent execution -> audit
```

要补：

- Tool registry：每个工具的权限、风险、credential scope、是否需要审批、是否需要 dry-run。
- Approval owner、expiry、reject/escalation、decision reason。
- Dry-run preview：展示将要做什么，但不泄露原始敏感 body。
- DB-backed transactional outbox。
- Idempotency key 和 side-effect receipt。
- Restart 后 pending approval 不丢、重复 approve 不重复执行。

### 4. Project 3 补外部 trace/eval 闭环

目标：

```text
trace -> review -> eval candidate -> regression -> release decision
```

要补：

- OTel spans：API、retrieval、model、tool、approval、audit、eval、release decision。
- Phoenix 或 Langfuse local backend。
- token/cost/latency/error metrics。
- 人工 reviewed failure trace 进入 eval fixture。
- failure clustering 和 reviewer label history。

### 5. 补生产形态部署和运维证明

目标：

```text
one-command production-shaped local stack
```

要补：

- API + frontend + worker + Postgres/pgvector + queue + OTel collector + optional observability backend。
- health/readiness 分离。
- backup/restore drill。
- 事故 runbook：ingestion failure、permission mismatch、eval regression、tool outage、trace export failure。
- load/failure tests：重启、并发审批、outbox crash recovery、connector timeout。

## 推荐对外表述

可以说：

```text
This is a production-minded reference implementation. It proves the invariants
I care about: permissions before generation, cited answers and abstention,
approval-gated side effects, action receipts, traces, audit logs, eval gates,
and trace-to-eval workflow.
```

不要说：

```text
This is already an enterprise production AI platform.
```

更准确的版本：

```text
This is the reference implementation I would use to discuss and then build the
production version. The remaining work is real identity, real connectors,
durable workers, external observability, and operational ownership.
```

## Sources

- OpenAI evaluation best practices: https://platform.openai.com/docs/guides/evaluation-best-practices
- OpenAI Agents SDK tracing: https://openai.github.io/openai-agents-js/guides/tracing/
- OpenAI prompt injection guidance: https://openai.com/index/designing-agents-to-resist-prompt-injection/
- Dify: https://dify.ai/
- FastGPT: https://fastgpt.io/
- MaxKB: https://docs.maxkb.pro/
- RAGFlow: https://github.com/infiniflow/ragflow
- LangGraph persistence: https://docs.langchain.com/oss/python/langgraph/persistence
- LangGraph interrupts: https://docs.langchain.com/oss/python/langgraph/interrupts
- Langfuse docs: https://langfuse.com/docs
- Phoenix docs: https://arize.com/docs/phoenix
- Ragas metrics: https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/
- OpenTelemetry GenAI semantic conventions: https://opentelemetry.io/docs/specs/semconv/gen-ai/
- OWASP Top 10 for LLM Applications: https://owasp.org/www-project-top-10-for-large-language-model-applications/
- NIST AI RMF official landing page
- NIST GenAI Profile: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf
