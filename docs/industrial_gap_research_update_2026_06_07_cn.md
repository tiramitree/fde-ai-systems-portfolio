# 工业可用距离判断与补强方案

Date: 2026-06-07

## 结论

当前仓库最准确的定位是：

```text
production-minded reference implementation, not production software
```

它已经是很强的 FDE / AI systems reference repo：能证明权限过滤、引用、拒答、审批、审计、trace、eval、release gate、公开仓库治理和生产升级路线。但它还不能诚实地说成“真实企业生产可用系统”。差的不是更聪明的 prompt，而是真实企业系统会要求的五层能力：

```text
真实数据平面 + 真实身份权限平面 + 持久运行平面 + 外部可观测/评测平面 + 运维责任模型
```

## 距离估计

| 目标 | 当前成熟度 | 判断 |
| --- | ---: | --- |
| FDE / AI systems 技术展示 | 90%-93% | 很强。能支撑对控制边界、eval、trace、治理、公开维护、生产取舍的深入讨论。 |
| 架构审查 / take-home artifact | 84%-88% | 可信。Production invariants 很清楚，但会被追问真实 auth、真实 source API、durable worker、外部 observability。 |
| 受控本地 demo | 80%-85% | 强。三套系统能稳定展示权限 RAG、引用/拒答、审批、审计、trace、eval、release gate。 |
| 低风险内部试点 | 45%-55% | 还不够。需要 SSO/OIDC、真实连接器、Postgres/pgvector、queue/worker、外部 trace/eval、runbook。 |
| 敏感企业生产 | 25%-35% | 距离明显。需要租户隔离、源系统 ACL 同步、DLP/PII、保留/删除、备份恢复、负载/故障测试、合规和 SRE ownership。 |

## 外部工业基线

这次对照的公开资料覆盖生产 RAG、Agent runtime、LLMOps、可观测性、安全治理和中国企业 AI 平台。

| Source | 看到的工业信号 | 对本仓库的含义 |
| --- | --- | --- |
| [OpenAI evaluation best practices](https://platform.openai.com/docs/guides/evaluation-best-practices) | 生产 LLM 应用需要围绕真实任务持续评测，而不是只看单次输出。 | 继续把 eval 当发布闸门；下一步要把 trace 回灌、人工复核、失败样本晋升做实。 |
| [OpenAI production best practices](https://platform.openai.com/docs/guides/production-best-practices) | 生产化要考虑安全、监控、成本、延迟、扩展和故障。 | 本地 deterministic path 很好，但还缺真实运行指标、限流、成本/Token 记录和部署韧性。 |
| [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/) | Prompt injection、sensitive disclosure、excessive agency、vector/embedding weaknesses、unbounded consumption 都是核心风险。 | 当前威胁模型方向正确；还要把控制扩展到 DLP、限流、工具权限、向量库滥用和残余风险登记。 |
| [NIST AI RMF / GenAI Profile](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf) | AI 风险管理覆盖 govern、map、measure、manage。 | 需要 owner、residual risk、incident response、retention/deletion、release accountability，而不只是技术 demo。 |
| [OpenTelemetry GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/) | GenAI traces 要覆盖 model/agent spans、events、metrics；输入/输出可能含敏感信息，需要过滤或截断。 | 当前 OTLP-shaped export 是好骨架；下一步要有真正 OTel instrumentation、redaction/sampling、token/cost/error metrics。 |
| [Phoenix](https://arize.com/docs/phoenix) | Trace 捕获 model calls、retrieval、tool use、自定义逻辑，并可做评测、人工标注、datasets、experiments。 | 应把本地 trace-to-eval 连接到 Phoenix/Langfuse 类后端，让失败 run 能外部查看、标注、重放和比较。 |
| [Ragas metrics](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/) | RAG 指标包括 context precision/recall、noise sensitivity、faithfulness；Agent 指标包括 tool call accuracy、agent goal accuracy。 | 当前 retrieval metrics 方向对，但数据集太小；要增加噪声、冲突、缺失答案、权限边界和工具调用指标。 |
| [EnterpriseRAG-Bench](https://github.com/onyx-dot-app/EnterpriseRAG-Bench) | 约 50 万企业文档、500 个问题，覆盖 Slack、Gmail、Drive、GitHub、Jira、Confluence 等，并包含噪声、近重复、过期和内部术语。 | 当前 fixture 太干净。下一跳可信度来自更大、更脏、更冲突的企业型检索评测集。 |
| [Dify](https://dify.ai/zh) | 强调生产级 agentic workflow、RAG pipeline、integrations、observability。 | 工业产品不是单个聊天页，而是工作流、知识库、工具集成、发布和监控平台。 |
| [FastGPT](https://fastgpt.io/) | 强调 enterprise AI delivery、hybrid retrieval、debugging/auditing、SSO/RBAC、private deployment。 | 中国企业场景尤其看重私有化、SSO/RBAC、混合检索、审计、业务系统集成和现场可控性。 |
| [MaxKB](https://maxkb.pro/) | 企业级 Agent 平台，包含 RAG pipeline、workflow、MCP tool-use、多模型。 | 国内企业平台趋势是“知识库 + 工作流 + 工具调用 + 多模型/私有模型”。 |
| [Onyx connectors/permissions](https://docs.onyx.app/overview/core_features/internal_search) | 企业知识检索要同步 documents、metadata、permissions，并接近实时保持更新。 | Project 1 最关键的工业缺口是源系统连接、ACL 同步、删除/更新证明和用户级可见性。 |
| [Microsoft Agent Governance Toolkit](https://opensource.microsoft.com/blog/2026/04/02/introducing-the-agent-governance-toolkit-open-source-runtime-security-for-ai-agents/) | Agent runtime security 重点是 policy、identity、audit、sandboxing、SRE。 | Project 2 的审批方向正确，但要继续补工具身份、策略引擎、执行沙箱、审计链和故障恢复。 |

## 当前强项

| 领域 | 已有证据 | 为什么重要 |
| --- | --- | --- |
| 安全不变量 | 权限在生成前过滤；模型不是安全边界；Project 2 副作用要审批。 | 比普通 RAG/Agent demo 强，因为风险控制在应用层。 |
| Project 1 数据骨架 | Admin ingestion、source sync、source bundle、GitHub read connector、job ledger、parser metadata、source scan、ACL snapshot、source lifecycle。 | 已经开始像数据接入系统，而不是静态 seed demo。 |
| 检索质量 | local hybrid scoring、reranker boundary、citation spans、recall@k、MRR、nDCG@k、ranked context precision、citation alignment、permission block、stale-source filtering。 | 能检查 retrieval，而不是只看 final answer。 |
| Project 2 治理 | Approval queue、side-effect blocking、dry-run preview、action outbox、retry/dead-letter、worker lease、action receipt。 | 进入了企业 agent 的核心模式：AI 提议，系统/人批准，持久执行，审计留痕。 |
| Project 3 可靠性 | Eval failure -> incident -> release block -> remediation -> regression。 | 能讲清 AI app 发布不是改完 prompt 直接上线。 |
| 公开维护 | README、API docs、evidence matrix、threat model、CI、public safety scan、PR policy、visual assets。 | 对技术审查很有价值，说明不是孤立 demo。 |

## 主要差距

| Gap | 当前状态 | 工业目标 |
| --- | --- | --- |
| 数据接入/解析 | 本地 seed、admin ingestion、source bundle、GitHub issue/PR intake、parser/scanner contract。 | 真实 connector、PDF/DOCX/table/OCR、增量同步、source span、parser worker、删除/失效证明。 |
| 身份/权限 | Fictional users、local signed token、角色/组、ACL snapshot、Postgres RLS artifacts。 | SSO/OIDC、真实租户/用户/组、源系统 ACL sync、RBAC/ABAC、permission drift alert、live RLS tests。 |
| 检索/引用 | 小型 deterministic corpus、hybrid scoring、reranking、citation alignment。 | 生产 embedding/reranker、metadata filters、query routing、大规模噪声/冲突/缺失答案 eval。 |
| 运行持久性 | JSON 默认、可选 Postgres path、局部 outbox。 | Durable Postgres/pgvector、queue/worker、transactional outbox、crash recovery、backup/restore、failure/load tests。 |
| 工具执行治理 | 审批、拒绝/过期、outbox、receipt。 | Scoped credentials、policy engine、审批 owner/escalation、idempotent connector execution、compensation、sandboxing。 |
| Observability/EvalOps | Local traces/audit/evals、OTLP JSON、trace-to-eval candidates、reviewed eval ledger。 | OTel SDK spans、Phoenix/Langfuse/OpenAI eval backend、dashboards、alerts、token/cost/latency/error、human labels、failure clustering。 |
| 安全/治理 | Threat model、safety scan、redaction、governance registry。 | DLP/PII、secret manager、retention/deletion、red-team program、incident runbooks、residual-risk register。 |
| 部署/运维 | Local apps、Docker static checks、docs。 | Production-shaped stack：API、frontend、worker、Postgres/pgvector、queue、OTel collector、auth middleware、rollback、runbooks。 |

## 推荐升级路线

### P0: 先保持定位诚实

- 公开表述保持：`production-minded reference implementation, not production software`。
- 不把 Docker/OpenAI/branch protection/release page/manual settings 说成已经完成，除非对应检查或手动证据存在。
- 每次安全敏感改动跑：`python -B scripts/dev.py governance-controls`、`python -B scripts/dev.py threat-model`、`python -B scripts/dev.py quality`。

### P1: 做一个真正的数据平面切片

目标链路：

```text
source -> parse -> chunk -> embed -> index -> retrieve -> cite -> eval -> trace
```

优先选一个高价值 source：local folder、GitHub repo content、Drive-like bundle 三选一，做深，不要三个都浅。

验收：

- Allowed user 能拿到 citation-backed answer。
- Blocked user 不能 retrieve restricted evidence。
- Deleted/stale source 不再出现在 retrieval/citation。
- Failed ingestion job 有 retry/dead-letter/operator recovery evidence。

### P2: 身份和权限同步可信化

目标：

```text
same corpus, different authenticated users, different retrievable evidence
```

要补 OIDC-compatible middleware contract、tenant/user/group/source principal 分离、source ACL drift test、Postgres live RLS test。

### P3: Project 2 做 durable governed action runtime

目标：

```text
agent proposes -> dry-run preview -> approval -> transactional outbox -> idempotent execution -> audit
```

要补 DB-backed outbox、idempotency key、approval owner/expiry/escalation、scoped credentials、connector-specific retry/dead-letter/compensation。

### P4: 外部 trace/eval 闭环

目标：

```text
trace -> review -> eval candidate -> regression -> release decision
```

要补 OTel SDK instrumentation、Phoenix/Langfuse local backend path、token/cost/latency/error metrics、human label history、failure clustering。

### P5: 生产形态本地栈

目标：

```text
one-command production-shaped local stack
```

组成：API apps、frontend、worker、Postgres/pgvector、queue、OTel collector、optional observability backend、auth middleware、health/readiness、backup/restore drill、rollback plan、incident runbook。

## 下一步最应该做的工程动作

最短路线不是继续堆新页面，而是按这个顺序补：

1. API runtime hardening：统一 request body size limit、基础 rate-limit/cost-limit、request id、structured safe error。
2. Project 1 数据平面：真实 local folder/GitHub repo content connector + parser/source-span/delete-proof。
3. Project 1 权限平面：OIDC contract + source ACL drift + live RLS proof。
4. Project 2 运行平面：DB-backed transactional outbox + idempotent execution + restart recovery。
5. Project 3 EvalOps：OTel/Phoenix path + trace review -> eval promotion。
6. Operator UX：统一查看 source health、jobs、ACL drift、retrieval metrics、approvals、outbox、traces、evals、release blocks。
7. Failure drills：connector timeout、worker crash、duplicate approval、stale source、permission mismatch、trace export failure、backup/restore。

## 对外讲法

可以说：

```text
This is a production-minded reference implementation. It proves the invariants:
permissions before generation, cited answers and abstention, approval-gated side
effects, action receipts, traces, audit logs, eval gates, and trace-to-eval workflow.
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
