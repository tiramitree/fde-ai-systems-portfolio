# Industrial Reality Check - 2026-06-07

本文件回答一个严格问题：

```text
这个 portfolio 项目距离真正工业可用的企业 AI 系统还差多远？
```

结论先行：

```text
它已经是很强的 FDE / AI systems portfolio 和架构技术评审材料。
它还不是可以直接承载真实敏感企业数据的工业产品。
```

## 当前定位

最诚实的外部说法：

```text
Production-minded reference implementation.
```

不要对外说：

```text
Production-ready enterprise AI platform.
```

原因是它已经证明了很多生产不变量，但还没有真实生产运行面。

已经很强的部分：

- 权限过滤发生在生成前，而不是靠 prompt 让模型自觉。
- 支持 citation、abstention、prompt-injection handling。
- 支持 admin ingestion、source sync、GitHub read connector、source bundle connector 这类数据接入边界。
- 有 ingestion job ledger、idempotency、retry lineage、dead letter、connector status、opt-in prune。
- 有 tool approval gate、trace、audit、eval、release gate。
- 有 public repo hygiene、CI、release evidence、threat model、API docs。

真正工业化还缺的部分：

- 真实 SSO / OIDC / tenant / group / source ACL 同步。
- 可持久运行的 Postgres / pgvector / queue / worker / backup / restore。
- 大规模真实格式文档解析：PDF、DOCX、表格、图片 OCR、多模态文档理解。
- 大语料检索质量指标：recall@k、MRR/nDCG、context precision/recall、citation faithfulness。
- 外部可观测系统：OpenTelemetry / Langfuse / Phoenix / LangSmith 级 trace、metric、alert、eval loop。
- 真正的外部 connector：Google Drive、Slack、Jira、Confluence、GitHub、Gmail、CRM 等，带权限同步和删除同步。
- 生产部署：API gateway、auth middleware、worker fleet、secret manager、rate/cost limit、incident runbook、SLA/ownership。

## 距离估计

| 目标 | 当前距离 | 大致成熟度 | 判断 |
| --- | --- | --- | --- |
| FDE / AI systems 技术评审作品 | 近 | 85%-90% | 已经足够讲系统设计、取舍、安全边界、eval、public maintenance。 |
| take-home / 架构 review | 近到中等 | 75%-82% | 很可信，但 reviewer 会追问真实身份、真实 source API、durable worker、live database。 |
| 低风险内部 pilot | 中到远 | 38%-48% | 需要真实 auth、durable DB/queue、真实 connector、外部 observability、operator runbook。 |
| 敏感企业生产环境 | 远 | 22%-32% | 需要完整 security/compliance/ops/incident/deployment/support model。 |

## 外部工业标杆扫描

这次外部扫描的共同结论是：工业级项目不是聊天 UI 更漂亮，而是围绕真实数据、真实身份、真实工具、真实故障建立控制面。

| 标杆 | 公开信号 | 对本项目的启发 |
| --- | --- | --- |
| OpenAI production best practices / agents / evals | 强调生产应用的安全、结构化输出、tool guardrails、trace、eval、业务上下文评测。 | 模型不能当安全边界；继续保留 application-level permission、approval、audit、eval。 |
| LangGraph | durable execution、checkpoint、human-in-the-loop、interrupt、memory、time travel debugging。 | Project 2 的审批概念对，但要升级成可恢复的持久 workflow，而不是内存态 demo。 |
| Langfuse / Phoenix / LangSmith | traces、sessions、prompt/version、dataset、experiment、LLM-as-judge、human annotation、monitoring。 | 当前 local trace 很好，但要接外部 backend，形成 trace -> eval -> regression 的闭环。 |
| RAGFlow | enterprise RAG engine、deep document understanding、template chunking、grounded citation、多源接入、多路召回、reranking、自托管。 | Project 1 要继续补 parsing、source span、hybrid retrieval、reranker、真实 source sync。 |
| Dify / FastGPT / MaxKB | 面向企业的 agent / workflow / RAG / knowledge base / private deployment / model-agnostic platform。 | 中国企业更看重私有化部署、业务系统集成、权限、可控 workflow、交付速度。 |
| Onyx / enterprise search RAG | connector、near-real-time indexing、metadata、permission sync。 | 数据连接器和权限同步是工业可信度的核心，不是附属功能。 |
| EnterpriseRAG-Bench | 大规模企业合成文档，覆盖 Slack/Gmail/Drive/GitHub/Jira/Confluence/HubSpot 等源，以及冲突、噪声、缺失、多文档推理。 | 当前语料太小；下一阶段要用大而乱的企业场景评测拉开可信度。 |
| OpenTelemetry GenAI conventions | GenAI span/event/metric/attribute，包括 token、model、agent、tool telemetry。 | local JSON trace 应升级为 OTel-compatible production telemetry。 |
| OWASP LLM / Agentic AI guidance | prompt injection、sensitive disclosure、insecure plugins/excessive agency、agent identity/privilege risk。 | Threat model 要映射到 OWASP case，并转成自动化安全 eval。 |
| NIST AI RMF / GenAI profile | 风险治理、measurement、management、documentation、accountability。 | 真正工业化要有风险 owner、残余风险、retention/deletion、incident response、release accountability。 |

## 当前最大优势

这个项目不是“算法炫技型”，而是“AI 系统工程型”。

技术评审里真正有价值的表达是：

```text
I built the control plane first.
The model is not the security boundary.
Permissions, citations, abstention, side-effect approval, traces, audit logs,
evals, and release gates are explicit in application code.
```

这对于 FDE、AI application engineer、AI platform engineer 比“我会调一个模型 API”强很多。

## 最大短板

最大短板不是某个算法没写，也不是 UI 不够漂亮。

最大短板是：

```text
还没有一条真实可运行的 industrial data plane。
```

也就是下面这条链还不够真：

```text
real enterprise source
  -> authenticated connector
  -> source ACL sync
  -> parser worker
  -> chunk/embed/index
  -> permission-aware retrieval
  -> cited answer
  -> trace/eval/alert
  -> operator recovery
```

目前我们已经开始补 connector/source sync/source bundle，但仍然偏 synthetic/local-first。

## 最短升级路线

不要平均强化三个项目。最正确的路线是把项目包装成：

```text
Enterprise AI Control Plane
```

三层叙事：

```text
Project 1 = production data spine
  ingestion -> ACL sync -> retrieval -> citations -> evals -> traces

Project 2 = governed action layer
  proposed action -> dry-run -> approval -> idempotent execution -> audit

Project 3 = reliability layer
  traces/eval failures -> incident -> release block -> remediation -> regression
```

优先级：

1. Project 1 做一条更真的生产数据面。
2. Project 2 做持久 workflow / approval / external tool execution。
3. Project 3 接 trace-to-eval-to-release 的真实闭环。

## Project 1 下一步

目标：

```text
source sync -> parse -> chunk -> embed -> index -> retrieve -> cite -> eval
```

需要补：

- 至少一个真实或准真实外部 connector：GitHub live、Google Drive fixture/live、Slack/Jira/Confluence mock-live 任选一到两个。
- parser worker：支持 TXT/Markdown/CSV/HTML 已有，继续补 DOCX/PDF/table/OCR 的生产形态。
- durable queue：ingestion 不再只是 inline worker，至少有 queue/job/retry/dead-letter 的可恢复模型。
- Postgres/pgvector live path：跑通一条 live DB 检索和 RLS 检查。
- source ACL drift：源权限变化后，旧 chunk 不再可检索。
- deletion/prune：源文件删掉后，检索结果和 citation 真的消失。
- retrieval eval：recall@k、context precision、faithfulness、permission leak、stale source filtering、conflicting docs。

验收证据：

- admin 同步一个 source 后，允许用户能问到并带 citation。
- 无权限用户不能看到，也不能在 trace/job/status 里泄漏正文。
- source 删除或 prune 后不能再被答案引用。
- 失败 job 进入 dead letter，可 retry，且不会重复写入。
- 所有上述行为进入 contract tests 和 evals。

## Project 2 下一步

目标：

```text
agent proposes action -> preview -> approval -> durable execution -> audit
```

需要补：

- workflow checkpoint：审批前后重启服务也能继续。
- approval owner / expiry / escalation。
- tool registry：每个工具有 scope、risk tier、dry-run schema、idempotency key。
- external tool mock-live：比如 ticket/CRM/email/calendar 至少一个。
- compensation behavior：执行失败后如何回滚或记录补偿动作。
- trace grading：评估 tool choice、approval compliance、unsafe bypass refusal。

## Project 3 下一步

目标：

```text
production trace -> reviewed eval candidate -> regression -> release decision
```

需要补：

- trace backend handoff：Langfuse/Phoenix/OpenTelemetry collector 任一条跑通。
- eval dataset ledger：哪些 trace 被人工审核后进入 eval。
- nightly regression / release gate。
- incident runbook：什么失败阻塞发布、谁审批例外、如何关闭。
- failure clustering：重复失败自动归类。

## Review Framing

如果被问“这能生产用吗”，最好的回答：

```text
I would not claim this is production software today.
I built it as a production-minded reference implementation.
The important part is that the invariants are already explicit:
permission before generation, grounded citations, abstention,
approval-gated side effects, trace/audit evidence, and eval gates.

To productionize it, I would keep those invariants and replace the local
runtime with SSO, Postgres/pgvector, durable workers, real source connectors,
OpenTelemetry-backed observability, larger retrieval evals, and operator
runbooks.
```

中文说法：

```text
我不会把它吹成已经能处理企业敏感数据的生产系统。
它现在是生产思维很强的 reference implementation。
核心价值是安全和质量边界已经写在应用代码里，而不是藏在 prompt 里。
真正工业化时，我会保留这些不变量，再替换身份、存储、队列、连接器、
观测、评测和运维层。
```

## 近期执行计划

最短能让它再上一个台阶的顺序：

1. 完成并提交 Project 1 source bundle connector，补齐 audit contract 和文档计数。
2. 跑完整 quality gate，确保 PR 状态干净。
3. 增加一个 live-ish connector 场景：GitHub live 或 Google Drive/Jira/Slack mock-live。
4. 跑通 Postgres/pgvector live demo path，包括 RLS 和 denied evidence count。
5. 增加 retrieval metrics 和大一点的 noisy enterprise corpus。
6. 接一个外部 trace/eval backend 的最小演示。
7. 再处理 Project 2 durable workflow。
8. 最后补部署/runbook/operator UX。

## Sources Checked

- OpenAI production best practices: https://developers.openai.com/api/docs/guides/production-best-practices
- OpenAI Agents guide: https://platform.openai.com/docs/guides/agents
- OpenAI evals / trace grading: https://platform.openai.com/docs/guides/evals
- LangGraph: https://github.com/langchain-ai/langgraph
- Langfuse: https://github.com/langfuse/langfuse
- Arize Phoenix: https://github.com/Arize-ai/phoenix
- RAGFlow: https://github.com/infiniflow/ragflow
- Dify: https://github.com/langgenius/dify
- FastGPT: https://github.com/labring/FastGPT
- MaxKB: https://github.com/1Panel-dev/MaxKB
- Onyx: https://github.com/onyx-dot-app/onyx
- Haystack: https://github.com/deepset-ai/haystack
- LlamaIndex: https://github.com/run-llama/llama_index
- EnterpriseRAG-Bench: https://github.com/PatronusAI/enterprise-rag-bench
- OpenTelemetry GenAI semantic conventions: https://opentelemetry.io/docs/specs/semconv/gen-ai/
- OWASP Top 10 for LLM Applications: https://owasp.org/www-project-top-10-for-large-language-model-applications/
- NIST AI RMF: https://www.nist.gov/artificial-intelligence
