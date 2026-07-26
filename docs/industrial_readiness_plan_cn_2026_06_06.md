# 工业可用性差距与升级方案

日期：2026-06-06

## 一句话结论

这个项目现在非常适合做 FDE / AI 应用工程 / 系统设计技术评审作品集，但距离“真实企业生产可用”还比较远。

更准确地说：

```text
它不是一个假装已经生产可用的项目，而是一个 production-minded reference implementation：
先把权限、引用、拒答、审批、审计、评测、发布闸门这些生产系统必须有的控制边界做出来，
然后再逐步把本地/模拟的数据面替换成真实企业基础设施。
```

## 粗略距离判断

| 目标 | 当前距离 | 判断 |
| --- | --- | --- |
| FDE 技术作品集 | 很近 | 已经能讲清楚“模型不是安全边界”、RAG、Agent 审批、eval gate、trace/audit、CI/release hygiene。 |
| 高质量 take-home / 架构 review | 较近 | 结构和故事可信，但最好补一个真正跑通的生产数据面切片。 |
| 低风险客户试点 | 中到远 | 已有 GitHub read connector 合约，但仍需要真实身份、Postgres/pgvector、文件/连接器 ingestion、外部观测、真实模型路径、运行手册。 |
| 真实企业生产系统 | 远 | 需要 SSO/租户隔离/权限同步/安全运营/备份恢复/在线评测/部署/告警/支持模型。 |

如果按“真实生产系统完整度”粗略打分，我会给：

| 维度 | 当前成熟度 |
| --- | --- |
| 作品集表达 | 80%-90% |
| 架构可信度 | 65%-75% |
| 可控内部 demo | 55%-65% |
| 受限 pilot | 30%-45% |
| 真正 production | 15%-25% |

这不是坏事。多数 GitHub 上看起来很炫的 AI 项目其实也停在 demo / template / reference 级别。我们这个项目的优势是控制边界比普通 demo 更认真，劣势是数据面、身份面、运行面还没有真正工业化。

## 搜索到的工业项目共同基线

工业级 RAG / Agent 项目反复出现同一套东西：

| 工业项目/资料 | 观察到的重点 | 对我们的启发 |
| --- | --- | --- |
| Microsoft Azure RAG 架构指南 | RAG 不是“chunk + embed + chat”这么简单，还要准备测试材料、chunking、metadata enrichment、embedding 选择、搜索策略、逐阶段评估。 | Project 1 需要真实 ingestion、chunk metadata、embedding provider、hybrid search、评测矩阵。 |
| Azure 信息检索指南 | 生产检索会考虑 vector/full-text/hybrid/manual multi-query、filter、query decomposition、reranking、HNSW 参数。 | 我们新增 reranker boundary 是对的，但还需要真实 pgvector/search 后端和检索指标。 |
| OpenAI eval/trace guidance | eval 是可靠 LLM 应用的核心；trace grading 用 end-to-end 决策、工具调用、推理步骤来做结构化评分。 | 当前静态 golden eval 很好，但要升级成 trace -> human label -> eval case -> release gate 的闭环。 |
| OpenAI Agents SDK HITL | 敏感工具调用应该 pause，等待人审批或拒绝，并可序列化恢复运行状态。 | Project 2 的审批方向正确，但需要 durable workflow state、idempotency、outbox、真实 connector。 |
| Langfuse / Phoenix | 企业 LLMOps 平台把 observability、prompt management、eval、dataset、annotation、trace debug 放在一起。 | 本项目已有 trace shape，但缺少外部 trace backend 和在线评测运营面。 |
| Dify | production-ready agentic workflow 平台通常包含 workflow、RAG pipeline、integrations、model management、observability。 | 真实产品不是三个孤立 demo，而是一个统一 operator surface。 |
| RAGFlow | 强调复杂文档解析、chunk 可视化、grounded citation、hybrid search、reranking、多数据源连接。 | Project 1 最大短板是文档解析、chunk/source span、复杂格式和大规模 corpus。 |
| Onyx | 企业搜索/RAG 重视 connector 和 permission sync，用户只能看到源系统允许看到的内容。 | 仅靠 UI 里选择 Alice/Morgan 不够，需要从 GitHub/Drive/Slack 等源同步 ACL。 |
| EnterpriseRAG-Bench | 企业 RAG benchmark 使用约 50 万文档、9 类企业来源、500 个问题，覆盖查找、推理、冲突、缺失信息。 | 我们的 seed corpus 太小，后续要做 realistic corpus 和 retrieval quality eval。 |
| production-ready FastAPI/LangGraph templates | 常见生产模板会包含 JWT、Postgres、Alembic、pgvector、Redis/Valkey、Langfuse、Prometheus/Grafana、rate limit、structured logging。 | 我们的应用控制做得好，但基础工程栈还需要补齐。 |
| 中国/全球 FDE 岗位要求 | RAG、Agent、Workflow、企业系统集成、可观测、评测、私有化/生产部署、业务流程改造是核心。 | 我们项目路线应偏“业务系统落地 + 治理 + 可解释交付”，而不是纯算法模型训练。 |

参考链接：

- Microsoft Azure RAG design guide: https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/rag/rag-solution-design-and-evaluation-guide
- Microsoft Azure RAG information retrieval: https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/rag/rag-information-retrieval
- OpenAI evals: https://developers.openai.com/api/docs/guides/evals
- OpenAI trace grading: https://developers.openai.com/api/docs/guides/trace-grading
- OpenAI Agents SDK HITL: https://openai.github.io/openai-agents-python/human_in_the_loop/
- Langfuse Enterprise: https://langfuse.com/enterprise
- Ragas production monitoring: https://docs.ragas.io/en/v0.1.21/getstarted/monitoring.html
- Dify: https://github.com/langgenius/dify
- RAGFlow: https://github.com/infiniflow/ragflow
- Onyx permission sync: https://docs.onyx.app/admins/connectors/official/github
- Onyx RAG/Search: https://docs.onyx.app/overview/core_features/internal_search
- EnterpriseRAG-Bench: https://arxiv.org/abs/2605.05253
- FastAPI LangGraph production template: https://github.com/wassim249/fastapi-langgraph-agent-production-ready-template

## 当前项目已经强的地方

| 能力 | 当前状态 | 为什么有价值 |
| --- | --- | --- |
| 权限边界 | Project 1 在 evidence 进入 answer 前做权限过滤。 | 技术评审时能讲清楚“不能靠 prompt 防泄漏”。 |
| 引用和拒答 | 有 citation-required answer 和 abstention 行为。 | 对企业知识问答很关键。 |
| Prompt injection 防护 | 有针对恶意文档/指令的安全场景。 | 说明你知道 RAG 的真实风险来自 retrieved context。 |
| Agent 审批 | Project 2 有 approval gate，不能直接执行副作用。 | 很贴近 FDE/企业 Agent 实际要求。 |
| 发布闸门 | Project 3 能把 eval failure 连接到 release block。 | 这比普通聊天 demo 更像生产工程。 |
| 评测和 CI | deterministic eval、quality gate、contract check、frontend check 都有。 | 说明不是只做 UI，而是有工程纪律。 |
| 文档和公开仓库卫生 | README、case study、threat model、API docs、visual assets、issue/PR/release hygiene 都有。 | 对 public GitHub 展示很有帮助。 |

## 当前真正短板

| 短板 | 现在缺什么 | 工业系统需要什么 |
| --- | --- | --- |
| 数据 ingestion | 主要是 seed documents 和本地模拟。 | 文件上传、PDF/DOCX/HTML/CSV 解析、OCR、表格、增量同步、失败重试。 |
| 检索质量 | 有 deterministic embedding、hybrid candidate、reranker boundary，但不是大规模真实检索。 | pgvector/search live path、hybrid retrieval、cross-encoder/LLM reranker、recall@k、faithfulness、stale/conflict eval。 |
| 权限同步 | 已有 fictional user/role、connector ACL snapshot、source permission ID、permission drift contract；还不是真实身份系统。 | SSO、租户、用户组、真实 source ACL sync、Postgres RLS live tests、permission drift tests。 |
| 持久化运行 | local JSON 是默认路径，已有本地 ingestion job ledger/idempotency/dead-letter/retry parent 证据，Postgres 还没完全 live 验证。 | Postgres connection pool、migrations、transactional audit、真实 worker queue、outbox、crash recovery。 |
| Agent connector | 工具是本地确定性函数。 | 真实 GitHub/Jira/CRM/Slack connector、credential scope、dry run、审批、幂等执行。 |
| 外部可观测 | 有 trace shape 和 OTLP-like export。 | OpenTelemetry SDK、Phoenix/Langfuse、dashboard、cost/latency/error/token metrics。 |
| 评测运营 | 静态 eval 很强，但还不是在线闭环。 | production trace sampling、human annotation、trace grading、nightly eval、model/prompt comparison。 |
| 安全合规 | threat model 和 safety tests 有基础。 | OWASP LLM Top 10 matrix、PII redaction、secrets manager、retention/deletion、incident runbook。 |
| 部署 | local-first。 | 云端 IaC、API gateway、health/readiness、backup/restore、rollback、load test、alerting。 |
| 管理台 | 三个 demo UI 分散。 | 一个统一 operator console：sources、permissions、traces、evals、approvals、incidents、release gates。 |

## 最优产品方向

不要把三个项目平均工业化。那样会越做越散。

最好的方向是：

```text
Project 1 = 生产主干
企业知识 ingestion + 权限 + 检索 + 引用 + 拒答 + trace + eval

Project 2 = 治理动作层
基于上下文提出操作，但所有副作用都经过 preview、approval、idempotency、audit

Project 3 = 可靠性/发布层
把 eval failure、bad trace、release risk、incident review 串起来
```

最终讲成一个产品：

```text
Enterprise AI Control Plane

sources + permission sync
  -> ingestion / parsing / indexing
  -> permission-aware RAG
  -> governed agent actions
  -> approval queue
  -> traces / audit / evals
  -> release gates / incident review
```

这个故事比“三个 AI demo”强很多，也更贴近 FDE。

## 下一步升级路线

### 1. 先把 Project 1 的生产数据面做成

目标：从 seed data 变成真实可上传、可解析、可检索、可引用、可评测。

要补：

- 文件上传 API。
- Markdown/TXT/CSV/HTML/DOCX/PDF parser。
- chunk metadata：source uri、title、section、page/span、version、tenant、ACL。
- embedding job。
- Postgres/pgvector live adapter。
- hybrid keyword + vector retrieval。
- reranker provider boundary。
- citation span。
- permission leak eval。

验收：

- 上传一个文档后能问答。
- 答案引用到具体 chunk/source。
- 没权限的用户不能拿到内容。
- 没证据时拒答。
- eval 里能测 recall@k、faithfulness、abstention、permission leak。

### 2. 做真实身份和权限

目标：不要再靠 UI 选择用户，而是系统真的知道当前用户是谁、属于哪个租户、有哪些源系统权限。

要补：

- auth middleware。
- tenant context。
- user/group/role model。
- source ACL model。当前已有 connector ACL snapshot 合约。
- Postgres RLS。
- permission sync fixture。当前已有本地 ACL snapshot fixture。
- permission drift eval。当前 API contract 已覆盖 ACL drift visibility change。

验收：

- 同一个 query，不同用户返回不同 evidence。
- 被过滤 evidence 只计数不泄漏。
- DB 层和 app 层都挡住越权访问。

### 3. 接外部观测和在线评测

目标：让系统不是“本地看日志”，而是能像生产系统一样被追踪、评分、回归。

要补：

- OpenTelemetry SDK spans。
- model/retrieval/tool/approval/eval span。
- Phoenix 或 Langfuse backend。
- trace URL 回写到 UI。
- trace grading。
- bad trace -> eval case。
- eval dataset versioning。

验收：

- 每个请求在外部系统里有 trace。
- 能按 tenant/user/model/retrieval profile/tool/action 查失败。
- 一个坏 case 能进入 eval 并阻止回归。

### 4. 加固第一个 read-only connector

目标：把已经存在的 GitHub read connector 从可审查合约推进到更接近真实企业知识来源。

已经有：

- `POST /api/connectors/github/sync`。
- fixture 模式用于 CI 稳定验证。
- live 模式可走 GitHub REST issues/pulls API。
- issue/PR 会转成 source sync ingestion job。
- 记录 source URL、external ID、ACL snapshot、idempotency、audit 和 citation。

继续补：

- incremental cursor。
- source permissions。
- 本地 full snapshot deletion/prune 已有，下一步是接真实外部源 API 的删除验证。
- backfill status。
- connector health。

验收：

- 能同步 GitHub issues/PRs。
- 能问项目相关问题。
- citation 指向原始 issue/PR URL。
- 没权限的数据不会出现在 retrieval 中。

### 5. 接一个 governed write connector

目标：证明 Agent 不只是聊天，而是能安全地改业务系统。

优先候选：

- GitHub issue comment。
- Jira/Linear ticket update。
- CRM note draft。

要补：

- tool registry。
- schema validation。
- dry-run preview。
- approval queue。
- idempotency key。
- transactional outbox。
- retry policy。
- audit event。

验收：

- Agent 只能提出操作，不可直接执行。
- supervisor approve 后才执行。
- 重复 approve 不会重复写。
- 拒绝/超时/失败都可审计。

### 6. 建统一 operator console

目标：把三个项目从 demo 变成一个系统。

页面应包括：

- Sources / sync status。
- Permission audit。
- Retrieval/eval dashboard。
- Trace explorer links。
- Approval queue。
- Incident/release gate。
- Cost/latency/token metrics。

验收：

- 评审者一打开就能看懂：这个系统怎么接数据、怎么控制权限、怎么观察、怎么评测、怎么审批、怎么发布。

## 最该避免的错误

不要继续堆“看起来像 AI 功能”的 demo。

不要现在就追求：

- 多 Agent 花活。
- 复杂 UI 炫技。
- 更多模拟业务场景。
- 声称 production-ready。
- 在没有真实 eval 的情况下换更复杂模型。

真正能把项目拉开差距的是：

```text
真实数据面 + 权限同步 + 评测闭环 + 外部观测 + 一个真实 connector + 安全审批执行
```

## 技术评审时应该怎么讲

推荐说法：

```text
这个项目我没有把它包装成已经 production-ready 的产品。
我先做的是生产 AI 系统最容易被忽视、但最关键的控制边界：
模型不负责权限，应用层过滤 evidence；
没有证据就拒答；
所有答案要有 citation；
Agent 不能绕过审批做副作用；
eval failure 会阻止 release；
trace 和 audit 能解释系统为什么这么做。

如果继续工业化，我会优先把 Project 1 做成生产主干：
真实 ingestion、Postgres/pgvector、source ACL sync、hybrid retrieval、reranker、OpenTelemetry、在线 eval。
然后让 Project 2 成为 governed action layer，Project 3 成为 release/reliability layer。
```

这套讲法诚实，而且显得很懂真实企业 AI 落地。
