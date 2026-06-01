# Hard Interview Playbook

Use this document to prepare for difficult FDE, AI application engineer, and solution engineering interviews.

## 1. Two-Minute Portfolio Pitch

I built two runnable enterprise AI systems.

The first is a secure enterprise knowledge copilot. It is not a basic RAG demo. It enforces role-aware retrieval before answer generation, requires citations, abstains when accessible evidence is missing, detects prompt injection inside retrieved documents, and records traces, audit events, and eval results.

The second is a governed customer operations agent for product-recall compliance. It can investigate cases, search policies, inspect listings, create internal violations, draft seller notices, and schedule follow-up. But it cannot send external notices or escalate cases directly. Those side-effect actions go through a supervisor approval queue, with idempotency, audit logs, traces, and unsafe-action evals.

Together they show the FDE pattern I care about: translate a real workflow into a deployable AI system, implement the controls around the model, and prove behavior with evals and traces.

## 2. System Design Questions

## Q1: Why not just use a vector database and ask the model to obey permissions?

Because permission enforcement must not depend on model obedience. The retrieval layer filters by tenant and role before evidence assembly. The model never sees documents the user cannot access. This reduces leakage risk and makes permission behavior testable.

## Q2: How do you handle prompt injection in RAG?

The system treats retrieved documents as data, not instructions. It detects instruction-like lines in retrieved chunks, removes them from evidence, records a security event, and can abstain if the remaining evidence is insufficient. In production I would combine pattern checks, document provenance scoring, model-based classifiers, and red-team evals.

## Q3: Why include abstention?

Enterprise users need correctness boundaries. If the system cannot find accessible evidence, unsupported answers are worse than no answer. Abstention also gives a measurable failure mode: false confident answer rate, abstention precision, and missing evidence categories.

## Q4: What are the most important evals?

For Project 1:

- permission leak evals
- required citation evals
- unsupported question abstention evals
- prompt injection evals

For Project 2:

- direct side-effect prevention
- approval compliance
- tool selection correctness
- policy citation correctness
- bypass prompt refusal

## Q5: Why keep approval outside the model?

The model can classify, draft, or recommend. It should not be the source of truth for whether a side-effect action is allowed. Approval enforcement belongs in deterministic application code because it must be auditable, testable, and consistent.

## Q6: What would you productionize first?

I would productionize the boundaries before adding model complexity:

1. real auth
2. PostgreSQL with row-level security
3. trace/audit persistence
4. eval CI gate
5. connector permission model
6. OpenAI Responses API or Agents SDK integration
7. observability and cost tracking

## Q7: What metrics matter?

Project 1:

- retrieval recall@k
- citation validity
- groundedness
- abstention precision
- false confident answer rate
- permission leak count
- latency and cost

Project 2:

- task success rate
- tool selection accuracy
- approval compliance
- unsafe action rate
- escalation correctness
- human intervention rate
- trace failure categories

## Q8: What are the biggest weaknesses in the current version?

The current version is intentionally local-first and dependency-free. It does not yet have real auth, PostgreSQL, dense embeddings, external connectors, or verified Docker runtime. Those are production adapters, not changes to the core control design. The important boundaries are already explicit: permission filter before generation, approval gate before side effects, traces, audit, and evals.

## 3. Deep Technical Tradeoffs

## Local Deterministic Mode vs OpenAI Mode

Local deterministic mode makes demos reliable and evals reproducible. OpenAI mode improves language quality and routing flexibility. The project supports both, but keeps safety enforcement in application code.

## JSON Store vs PostgreSQL

JSON store is good for zero-dependency demo reliability. PostgreSQL is required for production concurrency, indexing, transactions, row-level security, migrations, and audit durability.

## Keyword Retrieval vs Vector Retrieval

Keyword retrieval is deterministic and easy to inspect. Vector retrieval improves semantic recall. Production should use hybrid retrieval with metadata filters, reranking, and evals that catch both misses and over-retrieval.

## Single Agent vs Multi-Agent

For regulated workflows, I prefer a small orchestrator with explicit tools and deterministic gates. Multi-agent setups can help with specialization, but they also increase debugging and governance complexity. I would only split agents when there is a clear ownership boundary.

## 4. Whiteboard Architecture

```text
User
  -> UI
  -> API
  -> Auth / role / tenant
  -> Retrieval or Tool Planner
  -> Deterministic Policy Gate
  -> Model Gateway
  -> Trace Logger
  -> Audit Logger
  -> Eval Runner
```

Important explanation:

- The model is inside the system boundary, not the whole system.
- Security gates sit before and after model calls.
- Evals and traces are part of the product, not external test utilities.

## 5. Strong Closing Answer

The main thing I would emphasize is that I do not treat LLM integration as the hard part by itself. The hard part is making the workflow reliable enough for enterprise use: permissions, evidence, tool boundaries, approval, audit, traces, evals, and rollback. These projects are built to demonstrate that mindset.

