# 工业可用距离评估与补齐方案

日期：2026-06-06

这份记录回答一个问题：这个仓库距离真正工业可用还有多远，以及接下来应该按什么优先级补齐。

## 结论

当前项目已经是很强的 FDE / AI systems portfolio，不是普通 chatbot demo。它已经能展示权限过滤、引用、拒答、审批、审计、trace、eval gate、release blocking、CI 和公开仓库治理。

但它还不能诚实地称为工业生产系统。它更准确的定位是：

```text
production-minded reference implementation
```

也就是：关键控制边界已经设计出来并能跑通，但生产数据面、身份面、运行时、观测后端、连接器生命周期、部署和运维责任模型还没完全落地。

## 距离判断

| 目标 | 距离 | 判断 |
| --- | --- | --- |
| FDE 技术评审 / 技术展示作品 | 很近 | 已经能说明你理解企业 AI 系统真正难点，不只是 prompt。 |
| 系统设计 / take-home review | 近到中等 | 需要一个真实 production data-plane slice 来压实可信度。 |
| 低风险内部 pilot | 中等偏远 | 需要真实 auth、Postgres/pgvector、ingestion pipeline、观测后端、至少一个真实 connector。 |
| 敏感企业数据生产上线 | 远 | 需要 SSO、租户隔离、源系统 ACL 同步、安全运营、备份恢复、在线 eval、incident runbook、云部署和 owner model。 |

## 2026-06-06 全网再扫后的校准

这次继续横向看了 Dify、RAGFlow、Langfuse、Phoenix、TensorZero、Harness Evals、OpenAI Agents/Evals、OpenTelemetry GenAI、OWASP LLM Top 10、NIST AI RMF 等公开工业参考后，判断没有改变，但优先级更清楚了：

```text
本项目已经明显超过普通 AI demo。
它现在最像一个生产控制边界参考实现，而不是一个真实可上线产品。
真正要往工业可用推进，不该继续加新 demo，而该把现有控制边界接到真实数据、真实身份、真实观测、真实 connector 和真实运行时。
```

外部项目反复证明一个事实：工业 AI 系统不是“模型 API + UI”，而是一个可运营系统。成熟项目通常同时覆盖模型网关、RAG 数据面、工具治理、trace/eval、prompt/dataset 管理、审批、人审、部署、监控、成本和安全治理。TensorZero 把 gateway、observability、evaluation、optimization、experimentation 放在一起；Phoenix 和 Langfuse 把 traces、datasets、experiments、prompt management 放在一起；RAGFlow 强调复杂文档解析、chunk 可解释、grounded citation、heterogeneous data source、multiple recall 和 reranking；Dify 把 workflow、RAG、agent、model management、observability 和 API 作为一个平台 surface。

所以本项目的真实差距不是“功能少几个按钮”，而是这些工业平面的缺口：

| 工业平面 | 当前状态 | 到生产还缺什么 |
| --- | --- | --- |
| 数据面 | Project 1 有 seed data、admin ingestion、source span、local embedding boundary、SQL candidate、reranker boundary。 | 文件/connector ingestion、parser worker、OCR/table、incremental sync、生产 embedding/reranker、live pgvector/search 验证、大 corpus eval。 |
| 身份权限面 | 应用层有 permission-before-generation、demo 用户/角色、connector ACL snapshot、permission drift evidence。 | SSO、tenant/user/group、真实 source ACL sync、Postgres RLS live tests、permission drift detection。 |
| 运行时 | local JSON 是默认，Postgres 路径是 opt-in/部分验证；已有本地 ingestion job ledger、idempotency、dead-letter、retry parent 证据。 | connection pool、migrations live proof、真实 queue、scheduled retry、transactional outbox、crash recovery、backup/restore。 |
| Agent 工具面 | Project 2 有 approval gate 和 side-effect blocking。 | 真实 tool registry、scoped credentials、dry-run preview、approval owner/expiry/escalation、idempotent execution、connector outage handling。 |
| 观测面 | 本地 trace/audit 和 OTLP JSON handoff 已经有形状。 | OpenTelemetry SDK spans、Phoenix/Langfuse/OpenAI traces、dashboard、sampling、cost/latency/token/error metrics、PII redaction before export。 |
| EvalOps | golden eval 和本地 trace-to-eval candidate workflow 正在补齐。 | human labeling、review disposition、dataset versioning、nightly regression、trace grading、model/prompt/retrieval comparison。 |
| 安全治理 | threat model、安全扫描、workflow security、public safety 已经强于普通作品集。 | OWASP LLM Top 10 控制矩阵、NIST AI RMF 映射、secret manager、retention/deletion、red-team cases、incident runbooks。 |
| 部署运维 | local-first、Docker/compose checks、CI hygiene。 | production-like compose stack、cloud IaC、API gateway、auth middleware、managed DB/search、worker fleet、alerts、rollbacks、load tests。 |
| Operator UX | 三个 demo UI 分散展示。 | 一个统一控制台：sources、sync health、permissions、traces、evals、approvals、incidents、release gates。 |

如果用“工业真实可用”来打分，当前大概是：

| 维度 | 当前成熟度 |
| --- | --- |
| FDE 作品集 / 技术展示 | 85%-90% |
| 架构 review / take-home 可信度 | 70%-80% |
| 可控 synthetic pilot | 45%-55% |
| 低风险真实内部 pilot | 30%-40% |
| 敏感企业生产上线 | 15%-25% |

这里的关键不是贬低项目，而是保护叙事。技术评审时应该说：

```text
I built the production invariants first: permission before generation, grounded citations, abstention, approval gates, audit, traces, evals, and release blocking. I would not claim this is production software yet. The next industrial step is to replace local fixtures with real ingestion, identity, Postgres/pgvector, external observability, trace-to-eval operations, and governed connectors while preserving those invariants.
```

## 外部工业项目给出的基线

| 参考 | 工业信号 | 对本项目的含义 |
| --- | --- | --- |
| OpenAI production best practices | 生产化关注 API key 安全、组织隔离、staging/production project、限额、架构扩展。 | 我们要补 secret management、环境隔离、rate/cost/latency budget。 |
| OpenAI eval best practices | Q&A over docs 需要 context recall、context precision、answer quality，并持续评估。 | 现有 golden eval 不够，要加 retrieval metrics 和 trace-to-eval。 |
| OpenAI Agents SDK tracing / HITL | 工业 agent 要记录 generation、tool call、handoff、guardrail；敏感工具调用要可暂停审批并恢复执行。 | Project 2 的审批方向正确，但需要持久化 workflow state 和真实 tool connector。 |
| Dify | 把 workflow、RAG pipeline、agent、model management、observability 放在一个平台里。 | 我们后续要从三个 demo 合并成一个 operator/control-plane 叙事。 |
| RAGFlow | 强调复杂文档解析、可解释 chunk、traceable citation、多数据源、agent workflow。 | Project 1 需要真实解析、source span、hybrid retrieval、reranker、chunk 可审计。 |
| Onyx / EnterpriseRAG-Bench | 500K+ 企业文档、500 问、9 类企业来源、噪声/冲突/缺失信息。 | 当前小型 seed corpus 离真实企业 RAG 很远，必须扩 eval corpus。 |
| Azure Search OpenAI Demo | 云 RAG sample 使用 Azure AI Search/OpenAI/数据 ingestion/引用，但仍提醒生产前要补安全。 | 即使厂商 sample 也不直接等于 production；我们不要过度声称。 |
| AWS Generative AI Application Builder | 管理台、RAG、agents、guardrails、Cognito、API Gateway、CloudWatch、S3/DynamoDB/SQS。 | 工业项目需要 admin console 和云基础设施，不只是本地 app。 |
| Langfuse / Phoenix | trace、eval、prompt version、dataset、experiment、production examples 是 LLMOps 核心。 | 我们需要把本地 trace 接到外部观测系统，并让坏 case 进入 eval。 |
| LangGraph persistence | checkpoint 支撑 HITL、memory、time travel、fault-tolerant execution。 | 审批流要能跨进程/重启恢复，不能只在本地 JSON demo 里成立。 |
| OpenTelemetry GenAI conventions | GenAI 有 model span、agent span、metrics、events、provider conventions。 | trace 输出应按 OTel 语义约定落地，而不只是自定义 JSON。 |
| OWASP LLM Top 10 | prompt injection、insecure output、sensitive info、plugin/tool risk、excessive agency。 | threat model 要变成控制矩阵、测试、日志和 runbook。 |

## 当前优势

| 维度 | 已经做得好的地方 |
| --- | --- |
| 安全边界 | 没把模型当安全边界，权限和 side-effect 在应用层控制。 |
| RAG 控制 | Project 1 有 permission-aware retrieval、citation、abstention、prompt-injection handling、audit、eval。 |
| Agent 治理 | Project 2 有审批队列、side-effect blocking、supervisor approval、audit evidence。 |
| Release reliability | Project 3 能用 eval regression evidence 阻断不安全 rollout。 |
| 工程卫生 | README、docs、screenshots、CI、quality gate、GitHub hygiene、issue/PR policy 都完整。 |
| 升级路径 | 已经有 Postgres/pgvector schema、RLS、repository interface、本地 embedding、SQL candidate retrieval、reranker boundary。 |

## 最大差距

| 差距 | 现在的状态 | 工业要求 |
| --- | --- | --- |
| 真实 ingestion | 主要是 seed data 和本地/admin ingestion。 | 文件上传、source connector、parser worker、OCR/table、incremental sync、backfill、失败恢复。 |
| 检索质量 | 有 deterministic scoring、embedding boundary、SQL candidate、reranker boundary，但语料小。 | 生产 embedding/reranker、hybrid retrieval、recall@k、MRR/nDCG、citation faithfulness、stale-source eval。 |
| 权限身份 | UI 选择 fictional users/roles，但 source sync 已能接受 ACL snapshot 并验证 permission drift。 | SSO、tenant、group、RBAC/ABAC、真实 source ACL sync、RLS、permission drift detection。 |
| 持久运行时 | local JSON 默认，Postgres path 还在推进；本地 ingestion job contract 已覆盖 idempotency、dead-letter 和 retry parent。 | connection pool、migration、真实 queue、scheduled retry、outbox、crash recovery。 |
| Agent connector | 工具是本地 deterministic function。 | 真实 tool registry、scoped credential、dry-run preview、approval owner/expiry、idempotent execution。 |
| 观测 | 本地 trace 和 OTLP-like export。 | OTel SDK、Phoenix/Langfuse/OpenAI traces、dashboard、cost/latency/error metrics、trace sampling。 |
| eval ops | 静态 golden cases。 | trace-to-eval、human label、nightly regression、prompt/model comparison、failure clustering。 |
| 安全合规 | threat model 和 safety checks 已经不错。 | OWASP matrix、PII redaction、secret manager、retention/deletion、red-team runbook、incident response。 |
| 部署 | local-first + Docker/compose checks。 | 云 IaC、API gateway、auth middleware、managed DB/search、worker fleet、backup/rollback/load test。 |
| Operator UX | 三个独立 demo UI。 | 统一 admin console：sources、permissions、sync health、evals、traces、approvals、incidents、release gates。 |

## 推荐产品方向

不要平均工业化三个 demo。那样会变宽但变浅。

推荐路线：

```text
Project 1 = production spine
  source ingestion -> ACL sync -> hybrid RAG -> citations -> evals -> traces

Project 2 = governed action layer
  retrieved context -> proposed action -> dry-run preview -> approval -> idempotent execution

Project 3 = reliability layer
  traces + eval failures -> incident -> release blocking -> remediation -> regression tests
```

最终叙事应该是：

```text
Enterprise AI Control Plane
```

而不是三个散装 demo。

## 最优先补齐顺序

1. Project 1 真实数据面：parser/chunk/source span/embed/pgvector/hybrid retrieval/reranker/citation/eval。
2. 真实权限模型：tenant/user/group/source ACL/RLS/permission drift eval；当前先有本地 ACL snapshot 和 drift contract。
3. 外部观测：OpenTelemetry SDK -> Phoenix/Langfuse/OpenAI traces。
4. trace-to-eval：坏 trace 自动进入 eval dataset，支持 prompt/model/retrieval 比较。
5. 一个 read connector：GitHub、Google Drive、Confluence、S3-style storage 选一个。
6. 一个 governed write connector：GitHub issue comment、Jira/Linear update、CRM note draft 选一个。
7. 统一 operator console：sources、sync、permissions、evals、traces、approval、release gate。
8. OWASP/NIST 安全治理：PII redaction、secret manager、retention、red team、incident runbook。
9. production-like deployment：API、worker、Postgres/pgvector、queue、OTel collector、frontend、health/readiness、backup/rollback/load test。

## 接下来最值得做的工程切片

第一优先级不是继续加 demo，而是把 Project 1 做成一个可审查的 production data-plane slice：

```text
上传/同步文档
  -> parser normalize
  -> chunk with source span
  -> embedding job
  -> pgvector + lexical index
  -> hybrid retrieval
  -> reranker
  -> permission filter
  -> answer with exact citation span
  -> trace + audit
  -> retrieval/citation/permission eval
```

这个切片完成后，项目会从“很强的 portfolio demo”进入“可信 controlled-pilot architecture”的级别。

## 技术评审时的诚实说法

```text
I would not claim this is production software yet. I built it as a production-minded reference implementation. The important part is that the invariants are already in application code: permissions before generation, citations and abstention, side-effect approval, trace/audit evidence, and eval release gates. To make it industrial, I would replace the local state and seed data with authenticated multi-tenant Postgres/pgvector, real ingestion and source ACL sync, hybrid retrieval with reranking, OpenTelemetry traces feeding an eval loop, and a governed connector runtime with idempotent approvals.
```

中文版本：

```text
我不会说它现在就是生产系统。它现在是一个 production-minded reference implementation。核心价值是关键安全和质量不变量已经在应用代码里：先权限再生成、有引用和拒答、有 side-effect 审批、有 trace/audit、有 eval gate。真正工业化时，我会保留这些不变量，然后把本地状态和 seed data 换成多租户 Postgres/pgvector、真实 ingestion、源系统 ACL 同步、hybrid retrieval + reranker、OpenTelemetry 观测和可审批的 connector runtime。
```

## 参考链接

- OpenAI production best practices: https://developers.openai.com/api/docs/guides/production-best-practices
- OpenAI eval best practices: https://developers.openai.com/api/docs/guides/evaluation-best-practices
- OpenAI trace grading: https://developers.openai.com/api/docs/guides/trace-grading
- OpenAI Agents SDK tracing: https://openai.github.io/openai-agents-python/tracing/
- OpenAI Agents SDK human-in-the-loop: https://openai.github.io/openai-agents-python/human_in_the_loop/
- Dify: https://github.com/langgenius/dify
- RAGFlow: https://github.com/infiniflow/ragflow
- EnterpriseRAG-Bench: https://onyx.app/enterpriserag-bench
- EnterpriseRAG-Bench paper: https://arxiv.org/abs/2605.05253
- Azure Search OpenAI Demo: https://github.com/Azure-Samples/azure-search-openai-demo
- AWS Generative AI Application Builder: https://aws.amazon.com/solutions/implementations/generative-ai-application-builder-on-aws/
- Microsoft GraphRAG: https://www.microsoft.com/en-us/research/project/graphrag/
- Langfuse: https://github.com/langfuse/langfuse
- Phoenix: https://arize.com/docs/phoenix
- LangGraph persistence: https://docs.langchain.com/oss/python/langgraph/persistence
- OpenTelemetry GenAI semantic conventions: https://opentelemetry.io/docs/specs/semconv/gen-ai/
- OWASP LLM Top 10: https://owasp.org/www-project-top-10-for-large-language-model-applications/
