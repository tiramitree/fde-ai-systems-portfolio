# Technical Review Playbook

Use this document to evaluate the system design, safety boundaries, operational controls, and production upgrade path.

## 1. Two-Minute System Pitch

This repository implements three runnable enterprise AI reference systems.

The first system is a secure enterprise knowledge copilot. It enforces identity-aware retrieval before answer generation, requires chunk-level and sentence-level source-span citations, abstains when accessible evidence is missing, detects prompt injection inside retrieved documents, and records traces, audit events, and eval results.

The second system is a governed customer operations agent for product-recall compliance. It investigates cases, searches policies, inspects listings, creates internal violations, drafts seller notices, and schedules follow-up. External notices and escalations are deterministic side effects that go through a supervisor approval queue with idempotency, audit logs, traces, and unsafe-action evals.

The third system is an AI reliability incident console. It links canary incidents to failed eval cases, blocks unsafe rollout expansion, produces remediation plans, and records trace and audit evidence for release decisions.

Together they show the full control path around model-facing systems: secure data access, governed action, release reliability, observability, and regression testing.

## 2. System Design Questions

## Q1: Why not ask the model to obey permissions?

Permission enforcement must not depend on model obedience. The retrieval layer filters by tenant, role, and source-group identity before evidence assembly. The model never sees documents the user cannot access. This reduces leakage risk and makes permission behavior testable.

## Q2: How does the RAG system handle prompt injection?

Retrieved documents are treated as data, not instructions. The system detects instruction-like retrieved lines, removes unsafe evidence from the answer context, records a security event, and can abstain if the remaining accessible evidence is insufficient.

## Q3: Why include abstention?

Enterprise users need correctness boundaries. If the system cannot find accessible evidence, unsupported answers are worse than no answer. Abstention also gives a measurable failure mode: false confident answer rate, abstention precision, and missing-evidence categories.

## Q4: Why keep approval outside the model?

The model can classify, draft, or recommend. It should not be the source of truth for whether a side-effect action is allowed. Approval enforcement belongs in deterministic application code because it must be auditable, testable, and consistent.

## Q5: Why add a release reliability console?

Secure retrieval and governed tools are necessary before deployment, but AI teams also need operational controls after deployment. The reliability console shows how eval regressions, incident severity, runbooks, trace records, and audit events can block rollout decisions before user impact grows.

## Q6: What are the most important evals?

Project 1:

- permission leak evals
- required citation and citation-span evals
- unsupported question abstention evals
- prompt-injection evals

Project 2:

- direct side-effect prevention
- approval compliance
- tool selection correctness
- policy citation correctness
- bypass prompt refusal

Project 3:

- unsafe rollout blocking
- eval regression linkage
- latency-only monitor decisions
- remediation completeness
- audit and trace evidence creation

## Q7: What would be productionized first?

1. real authentication and authorization
2. PostgreSQL with row-level security
3. pgvector or hybrid retrieval
4. durable trace and audit persistence
5. CI/CD eval gates
6. connector permission model
7. OpenAI Responses API or Agents SDK integration
8. OpenTelemetry, cost, and latency observability

## Q8: How would a bad answer, unsafe action, or release decision be debugged?

Start from the response or decision `trace_id`, inspect retrieved evidence or tool calls, check linked audit events, and verify eval evidence. For the copilot, inspect retrieval filters, citation sets, abstain reasons, and security events. For the operations agent, inspect blocked actions, approvals, and idempotent execution. For the reliability console, inspect the incident, failed eval cases, rollout decision, remediation plan, trace records, and audit events.

## Q9: What is the threat model?

The threat model covers unauthorized disclosure, source-group permission drift, prompt injection, unsupported answers, unsafe side effects, approval bypass, duplicate side effects, secret or error leakage, public PR abuse, dependency drift, optional model gateway risk, observability gaps, UI serving surprises, and unsafe release rollout. Each risk has a deterministic control owner and an evidence command in `docs/threat_model.md`.

## Q10: What are the biggest current limitations?

The systems are intentionally local-first and dependency-light. Project 1 now has optional PostgreSQL/pgvector migration, seed, compose, repository, embedding, SQL candidate-retrieval, and deterministic reranker boundaries, but this environment still lacks live Docker/PostgreSQL validation, real auth, production embedding/reranker providers, external connectors, and a managed deployment. Those are production adapters; the core control boundaries are already explicit and testable.

## 3. Architecture Summary

```text
User
  -> UI
  -> API
  -> Auth / role / group / tenant
  -> Retrieval, Tool Planner, or Release Triage
  -> Deterministic Policy Gate
  -> Optional Model Gateway
  -> Trace Logger
  -> Audit Logger
  -> Eval Runner
```

Key principle:

- The model is inside the system boundary, not the whole system.
- Security gates sit before and after model calls.
- Release gates use deterministic eval and incident evidence.
- Evals and traces are part of the product, not external decoration.
