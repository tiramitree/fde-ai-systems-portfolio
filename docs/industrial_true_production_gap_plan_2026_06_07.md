# True Industrial Production Gap Plan

Date: 2026-06-07

This note is the current strict assessment after a fresh web scan of
production-oriented AI systems, RAG platforms, agent frameworks, LLMOps tools,
and AI governance references. It records what this repository already proves,
how far it is from true enterprise production use, and the shortest upgrade
sequence that preserves the existing safety and reliability invariants.

## Executive Judgment

Best public positioning:

```text
Production-minded reference implementation, not production software.
```

The repository is already strong for an FDE / AI systems portfolio because it
shows control boundaries around model calls:

- permission filtering before generation
- source-group ACLs and citation-ready evidence
- citations, abstention, and prompt-injection handling
- admin ingestion, source sync, source bundle sync, GitHub read connector, and
  ingestion job ledger
- approval-gated side effects, action outbox records, retry/dead-letter states,
  and action-run receipts
- traces, audit logs, evals, release blocking, and claim checks
- public repo safety, workflow security, threat model, and reviewed eval ledger

It is not yet ready for sensitive enterprise production because the local,
synthetic, dependency-light runtime still needs a real data plane, identity
plane, durable runtime plane, observability plane, governance program, and
operator model.

## Distance Estimate

| Target | Current maturity | Honest judgment |
| --- | ---: | --- |
| FDE portfolio / technical review artifact | 90%-93% | Very strong. The repo can support discussion of enterprise AI architecture, controls, evals, public maintenance, and production tradeoffs. |
| Architecture review / take-home artifact | 84%-88% | Credible. A reviewer can see the production invariants and upgrade path, but will still ask for real auth, source APIs, durable workers, and external observability. |
| Controlled synthetic demo | 78%-84% | Strong. The local demos can reliably show permission-aware RAG, approval gates, audit evidence, and release gates. |
| Low-risk internal pilot | 45%-55% | Not enough yet. Needs SSO/OIDC, durable Postgres/pgvector, queue/worker runtime, real connectors, external traces/evals, and runbooks. |
| Sensitive enterprise production | 25%-35% | Far. Needs source ACL sync, data retention/deletion, DLP/PII controls, secret management, compliance review, backup/restore, incident response, SLOs, load/failure tests, and owner model. |

The missing part is not another prompt or a prettier chat UI. It is:

```text
industrial data plane + identity plane + runtime plane + observability plane + operations model
```

## External Benchmark Scan

The scan favors primary or project-owned sources so the assessment is not based
on hype posts alone.

| Source | Public signal | Production meaning for this repo |
| --- | --- | --- |
| OpenAI production and eval guidance: https://platform.openai.com/docs/guides/production-best-practices and https://platform.openai.com/docs/guides/evaluation-best-practices | Production AI apps need secure access, robust architecture, latency/cost planning, and scenario-specific continuous evals instead of vibe checks. | Keep eval-driven development, add model/prompt/retrieval comparison, cost/latency/token metrics, and production deployment evidence. |
| LangGraph: https://github.com/langchain-ai/langgraph | LangGraph positions resilient agents around persistence, human-in-the-loop, memory, streaming, and debugging. | Project 2 approvals are conceptually right, but durable checkpoints and restart-safe workflows are still missing. |
| Dify: https://github.com/langgenius/dify | Dify is a production-ready agentic workflow platform combining workflows, RAG pipeline, agent capability, model management, observability integrations, self-hosting, and enterprise options. | Industrial products need admin/operator surfaces, model/provider management, deployment paths, and team workflows. |
| RAGFlow: https://github.com/infiniflow/ragflow | RAGFlow emphasizes deep document understanding, template chunking, grounded citations, heterogeneous data sources, multiple recall, fused reranking, self-hosting, memory, MCP, and agentic workflows. | Project 1 needs stronger parsing, source spans, PDF/DOCX/table/OCR handling, hybrid retrieval, reranking, and citation verification at scale. |
| BISHENG: https://github.com/dataelement/bisheng | BISHENG frames itself as an enterprise AI application DevOps platform with workflow, RAG, agents, model management, evaluation, dataset management, system management, and observability. | China-market FDE work values private deployment, workflow orchestration, knowledge-base operations, evaluation, and customer-facing system management. |
| R2R: https://github.com/SciPhi-AI/R2R | R2R positions itself as a production-ready AI retrieval system with agentic RAG and REST API. | A production RAG slice needs an API-level retrieval system, user/document management, ingestion, indexing, and operational controls. |
| EnterpriseRAG-Bench: https://github.com/onyx-dot-app/EnterpriseRAG-Bench | The benchmark uses more than 500,000 synthetic enterprise documents and 500 questions across Slack, Gmail, Linear, Drive, HubSpot, Fireflies, GitHub, Jira, and Confluence, including conflicts and info-not-found cases. | The current fixture set is too small. The next credibility jump is larger, noisier, conflict-heavy retrieval evaluation. |
| Phoenix: https://arize.com/docs/phoenix | Phoenix is an open-source observability and evaluation tool for tracing, datasets, experiments, prompt work, and LLM/RAG troubleshooting. | Local trace JSON should become OTel-backed traces plus datasets, human labels, experiments, and alerts. |
| LangSmith observability/evaluation: https://docs.langchain.com/langsmith/observability and https://docs.langchain.com/langsmith/evaluation | Production LLM apps are debugged through traces, metrics, datasets, experiments, evaluators, and feedback loops. | The repo has local trace/eval foundations; it needs online monitoring and trace-to-dataset operations. |
| Ragas metrics: https://docs.ragas.io/en/latest/concepts/metrics/available_metrics/ | Ragas lists RAG metrics such as context precision, context recall, noise sensitivity, response relevancy, faithfulness, plus agent/tool metrics. | Current retrieval metrics should expand to broader RAG and agent metrics over larger corpora. |
| OpenTelemetry GenAI conventions: https://opentelemetry.io/docs/specs/semconv/gen-ai/ | OTel defines GenAI spans, events, metrics, and attributes for model/agent telemetry. | Trace export should become full OTel SDK instrumentation around API, retrieval, model, tool, approval, audit, eval, and release decisions. |
| OWASP LLM Top 10: https://owasp.org/www-project-top-10-for-large-language-model-applications/ | OWASP tracks prompt injection, sensitive information disclosure, supply chain, data/model poisoning, improper output handling, excessive agency, system prompt leakage, vector/embedding weaknesses, misinformation, and unbounded consumption. | The threat model now needs a checked control registry mapped to OWASP/NIST, owners, evidence commands, and residual production risk. |
| NIST AI RMF and GenAI Profile: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf | NIST frames AI management through govern, map, measure, and manage. | Add ownership, residual exposure tracking, incident response, retention/deletion, monitoring, and release accountability. |
| AWS Generative AI Lens: https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/generative-ai-lens.html | AWS frames generative AI through architecture pillars including responsible AI, observability, and security. | A production claim needs cloud/runtime architecture evidence, not only local demos. |

## Current Strengths

| Area | Evidence in repo | Why it matters |
| --- | --- | --- |
| Security invariant | `docs/adr_0002_model_is_not_security_boundary.md`, `docs/threat_model.md`, Project 1 identity/retrieval/answering code, Project 2 tool guards | The app, not the model, decides permissions and side effects. |
| RAG data spine | Admin ingestion, source sync, source bundle connector, GitHub read connector, ingestion jobs, parser metadata, ACL snapshots, source lifecycle, prune semantics | The repo is moving beyond static seed data toward source-system operations. |
| Retrieval quality | `scripts/check_project1_retrieval_metrics.py` covering recall@k, MRR, nDCG@k, ranked context precision@k, citation alignment, security-event coverage, permission blocking, leak prevention, and stale-source filtering | It can inspect retrieval before trusting final answer text. |
| Governed actions | Approval queue, blocked direct side effects, action outbox, retry/dead-letter states, worker lease proof, action-run receipts | It demonstrates safe agent operations rather than autonomous side effects. |
| EvalOps loop | Trace-to-eval candidates, redaction, reviewed eval ledger, nightly regression workflow | It is beginning to look like an AI quality system, not one-off tests. |
| Public maintainability | README, evidence matrix, threat model, API docs, CI, safety scan, PR policy, screenshots, release docs | The repo is reviewable as a public engineering artifact. |

## Eight Production Gaps

| Gap | Current state | True industrial target |
| --- | --- | --- |
| 1. Data ingestion/parsing | Admin text/file-like ingestion, source sync, source bundle connector, GitHub read connector, job ledger, checked parser quality metadata | Real connectors, uploads, parser worker, PDF/DOCX/table/OCR/image handling, source spans, parser versioning, incremental sync, deletion/prune proof |
| 2. Identity/permissions | Fictional users, roles, groups, ACL snapshots, local token boundary, Postgres RLS artifacts | SSO/OIDC, tenants, real users/groups, source ACL sync, RBAC/ABAC, live RLS tests, permission drift alerts |
| 3. Retrieval/citation quality | Local hybrid scoring, deterministic embedding/reranker boundary, citation spans, retrieval metrics gate | Production embedding/reranker, hybrid profiles, metadata filters, query routing, large/noisy/conflicting corpus evals |
| 4. Runtime durability | Local JSON default, optional Postgres path, inline job behavior, local action outbox | Durable Postgres/pgvector, queue/worker fleet, transactional outbox, crash recovery, backup/restore, load/failure tests |
| 5. Governed tool execution | Approval queue, side-effect blocking, sanitized action outbox, receipts | Tool registry, scoped credentials, dry-run preview, approval owner/expiry/escalation, idempotent execution, compensation behavior |
| 6. Observability/EvalOps | Local traces/audit/evals, OTLP-shaped export, trace-to-eval candidates, reviewed eval ledger | OTel spans, Phoenix/Langfuse/OpenAI backend, dashboards, alerts, token/cost/latency/error metrics, human labels, failure clustering |
| 7. Security/governance | Threat model, safety scan, model gateway safety, redaction policy, AI governance control registry | PII/DLP controls, secret manager, retention/deletion, red-team program, incident runbooks, residual-risk register, compliance review |
| 8. Deployment/operator UX | Local apps, docs, screenshots, Docker checks | Production-like stack with API, frontend, workers, Postgres/pgvector, queue, OTel collector, auth middleware, health/readiness, rollback, runbooks |

## Recommended Product Shape

Do not industrialize three separate demos evenly. The stronger narrative is:

```text
Enterprise AI Control Plane
```

Composition:

```text
Project 1 = production data spine
  source ingestion -> ACL sync -> parser/chunk/embed/index -> retrieval -> citation -> eval/trace

Project 2 = governed action layer
  proposed action -> dry-run preview -> approval -> action outbox -> idempotent execution -> audit

Project 3 = reliability layer
  traces/eval failures -> incident -> release block -> remediation -> regression
```

## Upgrade Sequence

### P0: Keep controls honest and checkable

Work:

- Maintain the current wording: production-minded reference implementation, not production software.
- Keep `docs/ai_governance_control_registry.json` mapped to OWASP/NIST, threat IDs, evidence files, commands, and residual gaps.
- Run `python -B scripts/dev.py governance-controls`, `python -B scripts/dev.py threat-model`, and `python -B scripts/dev.py quality` before any security-sensitive change.

Acceptance:

- Every threat has at least one mapped control.
- Every control has an owner role, framework mapping, evidence files, evidence commands, and remaining production gap.
- The quality gate includes the governance-control check.

### P1: Build one real production data-plane slice

Goal:

```text
source -> parse -> chunk -> embed -> index -> retrieve -> cite -> eval -> trace
```

Work:

- Add a local-folder or authenticated GitHub repository content connector first.
- Define parser output with source URI, MIME type, parser version, content hash, page/section/span, ACL snapshot, and warnings.
- Keep `source_parser_quality_v1` checked with `python -B scripts/dev.py parser-quality` so parser provenance, line counts, section counts, table-like signals, and format-specific details stay visible before content reaches retrieval.
- Keep `source_scan_v1` checked with `python -B scripts/dev.py source-scan` so local source safety scan status, severity, finding counts, review requirements, and raw-match suppression stay visible before content reaches retrieval.
- Move ingestion jobs behind a worker boundary with retry/dead-letter and operator recovery.
- Run one live Postgres/pgvector path on a Docker-enabled machine.
- Prove prune/delete: removed source cannot appear in retrieval or citation.
- Add noisy, conflicting, near-duplicate, stale, and absent-answer evals.

Acceptance:

- Allowed user can get cited evidence.
- Blocked user cannot retrieve restricted evidence.
- Deleted source disappears from current retrieval.
- Failed ingestion job can be retried or dead-lettered with audit evidence.

### P2: Make identity and permission sync credible

Goal:

```text
same corpus, different authenticated users, different retrievable evidence
```

Work:

- Add OIDC-compatible middleware contract while keeping local deterministic mode.
- Persist tenants, users, groups, memberships, source principals, and source ACLs.
- Add permission drift tests after source ACL changes.
- Add live RLS test against Postgres.

Acceptance:

- User A can cite a document.
- User B cannot retrieve it.
- Denied evidence count is auditable without body/title/chunk leakage.

### P3: External observability and trace-to-eval loop

Goal:

```text
trace -> review -> eval candidate -> regression -> release decision
```

Work:

- Emit OTel spans for API, ingestion, retrieval, model, tool, approval, audit, eval, and release decisions.
- Add optional Phoenix or Langfuse local backend path.
- Add token/cost/latency/error metrics.
- Promote one reviewed failure trace into a checked-in eval case.

Acceptance:

- A failed run can be inspected outside the app.
- A reviewed trace becomes an eval case.
- The release gate blocks on that regression until fixed.

### P4: Durable governed action runtime

Goal:

```text
agent proposes -> preview -> approval -> persisted execution -> audit
```

Work:

- Add workflow checkpoint state or a LangGraph-like persisted run model.
- Promote action outbox to a transactional database.
- Add approval owner, expiry, escalation, rejection reason, and compensation notes.
- Add scoped tool credentials and dry-run preview contract.
- Add one safe write connector mock-live path, such as issue/comment/ticket update.

Acceptance:

- Restarting the service does not lose pending approvals.
- Re-approving does not duplicate side effects.
- Failed execution records a retry/dead-letter path.

### P5: Operator console and deployment hardening

Goal:

```text
operator can answer: what broke, who is affected, what evidence supports it, and what action is safe next
```

Work:

- Add a unified operator surface for source health, connector jobs, ACL drift, retrieval metrics, traces, evals, approvals, action outbox, release gates, and incidents.
- Build production-like compose stack: APIs, frontend, worker, Postgres/pgvector, queue, OTel collector, optional observability backend.
- Add health/readiness split, backup/restore drill, rollback plan, and incident runbook.

Acceptance:

- Fresh environment starts the full stack from documented commands.
- Runtime failure can be diagnosed from runbook, traces, and audit.
- Public claim remains honest: production-shaped local stack, not enterprise production deployment.

## Review Framing

Use this answer if challenged:

```text
This is not a fake production-ready claim. I built a production-minded
reference implementation that proves the invariants I care about:
permissions before generation, grounded citations, abstention, approval-gated
side effects, action receipts, traces, audit logs, eval gates, and trace-to-eval
workflow. The remaining work is real enterprise infrastructure: SSO/OIDC,
source ACL sync, durable workers, external observability, retention/deletion,
and incident ownership.
```

Do not say:

```text
This is already an enterprise production AI platform.
```
