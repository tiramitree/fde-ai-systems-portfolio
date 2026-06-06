# Current Industrial Readiness Assessment

Date reviewed: 2026-06-06

This note records the current judgment after comparing this repository with
public production-oriented RAG, agent, LLMOps, governance, and FDE references.
It is a decision record for the next engineering work, not a production claim.

## Short Verdict

The repository is already strong as an FDE / AI systems portfolio and technical
review artifact. It is not yet an industrial production product.

| Target | Current distance | Judgment |
| --- | --- | --- |
| FDE portfolio / technical-review artifact | Very close | The repo demonstrates the right enterprise AI control boundaries: permission-aware RAG, citations, abstention, approval gates, audit logs, traces, evals, release gates, CI, public repo hygiene, and upgrade notes. |
| Serious architecture review / take-home | Close | The architecture is credible and has a GitHub read connector plus ingestion job ledger, but a reviewer can still ask for live auth, durable workers, and real production retrieval evidence. |
| Controlled pilot on synthetic or low-risk internal data | Medium to far | Needs real auth, Postgres/pgvector live verification, parser/indexing workers, source permission sync, external observability, and one hardened live connector. |
| Production over sensitive enterprise data | Far | Needs SSO, tenant isolation, source ACL sync, security operations, online eval operations, backup/restore, cloud IaC, incident runbooks, support ownership, and compliance evidence. |

Most honest framing:

```text
This is a production-minded reference implementation. It proves important AI
application invariants, but the production data plane, identity plane, runtime
plane, observability backend, connector lifecycle, and operations model still
need to be built.
```

Approximate maturity:

| Dimension | Current maturity |
| --- | ---: |
| Portfolio narrative | 85-90% |
| Architecture credibility | 70-80% |
| Controlled local demo | 65-75% |
| Low-risk pilot readiness | 35-45% |
| True industrial production readiness | 20-30% |

## External Baseline Signals

| Reference | What it shows | Implication for this repo |
| --- | --- | --- |
| Azure Search OpenAI Demo | A serious cloud RAG sample includes app code, tests, infra, evals, deployment paths, and Azure AI Search / Azure OpenAI integration. Source: https://github.com/Azure-Samples/azure-search-openai-demo | A production RAG story needs real search infrastructure, deployment evidence, and tests beyond a local chat UI. |
| AWS GenAIOps hardening guidance | Moving from PoC to production requires reliability, security, continuous improvement, deep observability, layered testing/eval, and security controls. Source: https://docs.aws.amazon.com/prescriptive-guidance/latest/gen-ai-lifecycle-operational-excellence/preprod-hardening.html | The current repo has the right control idea; it still needs production operations and observability depth. |
| AWS generative AI foundational architecture | Production GenAI platforms use authentication, API gateway, microservices, extraction, chunking, vectorization, prompt management, queues, search, logging, storage, and security services. Source: https://github.com/aws-samples/generative-ai-applications-foundational-architecture | Our next work should build a real data plane and worker pipeline, not another isolated demo. |
| OpenAI AgentKit / Agents docs | Agent platforms now emphasize workflow versioning, connector registry, ChatKit UI, guardrails, evals, trace grading, tools, MCP, state, and observability. Sources: https://openai.com/index/introducing-agentkit/ and https://developers.openai.com/api/docs/guides/agents | The repo should evolve toward an operator/control-plane story: connectors, guardrails, eval loop, and traceable tool use. |
| OpenAI guardrails guidance | Tool guardrails should run around each custom function-tool invocation, especially in workflows with handoffs or delegated specialists. Source: https://openai.github.io/openai-agents-python/guardrails/ | Project 2's approval boundary is directionally right; tool-specific guardrails and durable execution are the next leap. |
| OpenAI trace grading / agent evals | Trace grading evaluates end-to-end decisions, tool calls, and reasoning steps to find workflow failures. Sources: https://platform.openai.com/docs/guides/trace-grading and https://platform.openai.com/docs/guides/agent-evals | Static golden evals should become a trace-to-eval operations loop with human review and regression scheduling. |
| LangGraph | Production agent frameworks emphasize durable execution and human-in-the-loop for long-running stateful agents. Source: https://github.com/langchain-ai/langgraph | Approval workflows should survive restarts and preserve state checkpoints. |
| CUGA enterprise agent harness | Enterprise agents need tool orchestration, planning, policies, evals, cost/performance tradeoffs, RAG scopes, policy systems, HITL, and cluster self-hosting. Source: https://github.com/cuga-project/cuga-agent | The repo needs policy/version management and production deployment surfaces before industrial claims. |
| OpenEAGO | Enterprise agent governance focuses on signed payloads, policy bundles, compliance metadata, deterministic routing, replayable state snapshots, audit trails, auth, encryption, circuit breakers, retries, and agent registry. Source: https://openeago.finos.org/ | Our governance story is good locally, but needs identity, policy bundles, replay, durability, and registry semantics. |
| WEF AI Agents in Action 2026 | Agent authorization should be auditable, enforceable, and accountable across the deployment lifecycle. Source: https://www.weforum.org/publications/ai-agents-in-action-a-playbook-for-trusted-adoption-authorization-and-scaling/ | The final product direction should emphasize accountable delegation, not autonomous magic. |
| China FDE job descriptions | Recent FDE roles ask for production-grade LLM/Agent applications, RAG systems, enterprise document/data integration, CRM/ERP/Data Warehouse integration, workflow automation, evaluation, latency, cost, Python/TypeScript/API work, cloud architecture, and customer communication. Sources: https://www.michaelpage.com.cn/job-detail/ai-forward-deployed-engineer%EF%BC%88fde%EF%BC%89/ref/jn-062026-7029518 and https://cn.linkedin.com/jobs/view/%E8%B1%86%E5%8C%85ai%E5%A4%A7%E6%A8%A1%E5%9E%8Bfde%EF%BC%88forward-deployed-engineer%EF%BC%89-%E7%81%AB%E5%B1%B1%E5%BC%95%E6%93%8E-at-%E5%AD%97%E8%8A%82%E8%B7%B3%E5%8A%A8-4330494778 | This portfolio should optimize for end-to-end customer workflow delivery, not pure algorithm-screen preparation. |

## Current Strengths

| Area | Evidence in repo | Why it matters |
| --- | --- | --- |
| Security boundary | The model is explicitly not the security boundary; permissions and side effects are enforced in application code. | This is the core enterprise AI principle reviewers care about. |
| Project 1 RAG controls | Permission-aware retrieval, citations, abstention, prompt-injection handling, admin ingestion, source sync, GitHub read connector, ingestion job ledger, connector status surface, traces, audit logs, evals. | Stronger than a normal RAG demo because it shows data-plane, operator, and evidence controls. |
| Project 2 agent controls | Tool side effects require approval and supervisor execution; unsafe bypasses are refused. | Aligns with modern agent governance and FDE enterprise workflows. |
| Project 3 reliability controls | Failed eval evidence can block unsafe release rollout and create remediation evidence. | Shows the "AI app changes need release gates" story. |
| Public repo hygiene | CI, API contracts, threat model, screenshots, safety checks, release docs, branch protection notes, PR review policy. | Makes the repo credible as a public artifact, not only a local project. |
| Production upgrade path | PostgreSQL/pgvector migrations, repository interfaces, OpenAI optional gateway, OTLP-shaped traces, production upgrade notes. | Shows a clear path from local reference implementation to production infrastructure. |

## Main Gaps To Industrial Usability

| Gap | Current state | Industrial requirement |
| --- | --- | --- |
| Data ingestion | Seed data plus admin/source sync/GitHub connector contracts. | Uploads, parsers for PDF/DOCX/HTML/CSV/images/tables, OCR, incremental sync, deletion/prune, backfills, worker retries, source versioning. |
| Retrieval quality | Deterministic local embeddings/reranker boundary and optional Postgres design. | Live pgvector/search backend, production embedding model, hybrid lexical/vector retrieval, reranker provider, recall@k, MRR/nDCG, faithfulness, citation-span and stale/conflict evals. |
| Identity and permissions | UI-selected fictional users and connector ACL snapshot contracts. | SSO/auth middleware, tenants, groups, source ACL sync, RBAC/ABAC, Postgres RLS live tests, permission drift detection. |
| Runtime durability | Local JSON default; ingestion job ledger exists but still inline/local. | Durable DB, connection pool, real queue, retry scheduling, transactional outbox, crash recovery, migration discipline, immutable audit retention. |
| Agent workflows | Deterministic local tools and approval gate. | Real tool registry, scoped credentials, dry-run previews, approval ownership/expiry/escalation, idempotent write connectors, connector outage handling. |
| Observability | Local traces, audit logs, OTLP-shaped export. | OpenTelemetry SDK spans, hosted/local collector, Phoenix/Langfuse/OpenAI traces, dashboards, latency/cost/token/error metrics. |
| Eval operations | Static golden eval cases. | Trace sampling, human labels, trace grading, nightly regression, model/prompt/retrieval comparison, red-team cases from failures. |
| Security/compliance | Good threat model and safety checks. | OWASP LLM Top 10 matrix, PII redaction, secrets manager, retention/deletion, incident response, audit immutability, connector credential governance. |
| Deployment | Local-first services and static Docker hygiene. | Cloud/local production stack, API gateway, managed DB/search, worker fleet, health/readiness, backups, rollback, load tests, alerting. |
| Operator UX | Three separate demos; Project 1 is gaining connector/job controls. | Unified operator console for sources, permissions, connector health, traces, evals, approvals, incidents, and release gates. |

## Recommended Product Direction

Do not industrialize all three projects equally. That creates breadth without
depth. Use one product spine:

```text
Enterprise AI Control Plane

Project 1: production spine
  sources -> permission sync -> ingestion/parser/index -> hybrid RAG
  -> citation-grounded answers -> traces/audit/evals

Project 2: governed action layer
  retrieved context -> proposed tool action -> dry-run preview
  -> approval -> idempotent execution -> audit

Project 3: reliability layer
  trace/eval failures -> incident review -> release blocking
  -> remediation -> regression tests
```

## Upgrade Sequence

1. Finish the Project 1 operator surface already in progress.
   - Show GitHub connector sync from the browser.
   - Show connector lifecycle health from job-backed status.
   - Show recent ingestion jobs and statuses.
   - Update frontend integrity/UI contract checks.
   - Refresh visual assets only if the UI intentionally changes.

2. Finish Project 1's production data-plane slice.
   - File upload or one real source connector.
   - Parser output contract.
   - Chunk metadata with source URI, title, section/page/span, hash, version, tenant, and ACL.
   - Embedding job.
   - Postgres/pgvector live path.
   - Hybrid search plus reranker hook.
   - Citation spans.
   - Permission-aware retrieval evals.

3. Make identity and permissions real enough.
   - Add local enterprise-auth stub first, not full SSO.
   - Model tenants, users, groups, memberships, source ACLs, and policy separately.
   - Add RLS-backed tests and permission drift cases.

4. Harden the GitHub read connector.
   - Durable cursor checkpoints.
   - Permission sync model.
   - Deletion/prune handling.
   - Connector health/backfill logs.
   - Authenticated live smoke proof when credentials are available.

5. Add external observability.
   - Emit real OTel spans for API, ingestion, retrieval, model, tool, approval, audit, and eval events.
   - Send traces to one backend.
   - Keep UI trace IDs linked to backend trace IDs.

6. Turn evals into an operations loop.
   - Add recall@k, citation coverage, abstention correctness, permission leak, stale/conflicting-info, and tool-safety metrics.
   - Promote bad traces into reviewed eval cases.
   - Compare model, prompt, and retrieval variants before release.

7. Add one governed write connector.
   - Best first option: GitHub issue comment or Jira/Linear ticket update.
   - Require dry-run preview, human approval, idempotency key, transactional outbox, retry policy, and audit event.

8. Build the unified operator console.
   - Sources/sync status.
   - Permission audit.
   - Retrieval/eval dashboard.
   - Trace explorer links.
   - Approval queue.
   - Release gate and incident state.

9. Add security/deployment hardening.
   - OWASP LLM Top 10 control matrix.
   - PII redaction before model calls and trace export.
   - Secrets manager pattern.
   - Retention/deletion workflow.
   - Backup/restore and incident runbooks.
   - Local production-like Docker Compose, then one cloud IaC target.

## What Not To Claim Yet

Do not claim these until matching evidence exists:

- Production-ready for real customer data.
- Enterprise secure beyond the current demo threat model.
- Scales to enterprise corpora.
- Live OpenAI production mode.
- Docker/Postgres runtime fully verified on this machine.
- Source permission sync.
- External observability platform integrated.
- Real governed write connector.

## Next Best Engineering Move

The highest-leverage next move is:

```text
Finish the Project 1 connector/operator surface, then complete one real
production data-plane slice: parser -> chunk metadata -> embeddings ->
pgvector/hybrid retrieval -> reranker -> citations -> permission evals.
```

That single slice moves the project from "excellent portfolio reference" toward
"credible controlled-pilot architecture."
