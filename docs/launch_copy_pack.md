# Launch Copy Pack

Use this after the GitHub repository is public and GitHub Actions is green. Before posting, run `python -B scripts/dev.py launch-assets` to check that the launch copy remains complete and does not claim unfinished external blockers.

## One-Line Pitch

```text
Two local-first enterprise AI systems showing secure RAG, governed agents, evals, traces, audit logs, and approval gates.
```

## Short Post

```text
I open-sourced a small FDE-style AI systems portfolio:

- Secure Enterprise Knowledge Copilot: permission-aware RAG with citations, abstention, prompt-injection handling, traces, audit logs, and evals.
- Regulated Customer Operations Agent: governed tool-calling workflow with approval queues, side-effect blocking, supervisor approval, traces, audit logs, and unsafe-action evals.

It runs locally without paid APIs, but includes optional OpenAI Responses API integration points and a production upgrade path.

The key design principle: the model is not the security boundary. Permissions, side-effect authorization, audit, traces, and evals live in application code.
```

## LinkedIn Post

```text
Most AI app demos stop at chat.

I wanted a portfolio that shows the parts enterprise AI deployments actually need around the model, so I built two runnable systems:

1. Secure Enterprise Knowledge Copilot
   - permission-aware retrieval
   - citations and abstention
   - prompt-injection handling for retrieved content
   - traces, audit logs, and evals

2. Regulated Customer Operations Agent
   - tool-calling workflow
   - approval queue
   - side-effect blocking
   - supervisor-only execution
   - traces, audit logs, and unsafe-action evals

Both run locally without paid APIs. The optional OpenAI path is configurable, but the important controls stay outside the model.

The design principle is simple: the model is not the security boundary.

Repo: <repo-url>
```

## X / Twitter Thread

```text
1/ I built a local-first enterprise AI systems portfolio.

Not another chatbot template. Two runnable demos:
- secure RAG
- governed agents
- evals
- traces
- audit logs
- approval gates

2/ Project 1: Secure Enterprise Knowledge Copilot.

Alice can ask about remote work and gets cited evidence.
Alice cannot access the finance retention plan, so the system abstains.
Morgan can access the same finance evidence and gets an answer.

3/ Project 2: Regulated Customer Operations Agent.

The agent can investigate a recalled product listing, create internal records, draft a seller notice, and schedule follow-up.
It cannot send the notice directly.
Supervisor approval is required.

4/ The main design principle:

The model is not the security boundary.

Permissions, side-effect authorization, audit, traces, and evals stay in application code.

5/ It runs locally without paid APIs and includes optional OpenAI Responses API integration points.

Repo: <repo-url>
```

## Hacker News Show HN

Title:

```text
Show HN: Local-first enterprise AI systems portfolio with secure RAG and governed agents
```

Body:

```text
I built a small local-first portfolio of enterprise AI control patterns.

It contains two runnable systems:

- Secure Enterprise Knowledge Copilot: permission-aware RAG with citations, abstention, prompt-injection handling, traces, audit logs, and evals.
- Regulated Customer Operations Agent: governed tool-calling workflow with approval queues, side-effect blocking, supervisor approval, traces, audit logs, and unsafe-action evals.

The repo is intentionally dependency-light so reviewers can run it locally without paid APIs. Optional OpenAI Responses API integration points are included, but the security and side-effect boundaries stay in application code.

The core idea is: the model is not the security boundary.

I would especially welcome feedback on the eval design, permission boundary, and governed-agent workflow.
```

## Reddit / Community Post

```text
I built a local-first enterprise AI reference repo focused on the controls around LLM apps:

- secure RAG with role-aware retrieval
- citations and abstention
- retrieved-content prompt-injection handling
- governed tool-calling agent
- approval gates for side effects
- traces and audit logs
- eval and smoke-test gates

It is intentionally not a production platform. It is a runnable reference implementation for patterns that come up in enterprise AI/FDE interviews and early AI product pilots.

Repo: <repo-url>
```

## Follow-Up Blog Outline

Title:

```text
The Model Is Not The Security Boundary
```

Outline:

1. Why chatbot demos fail enterprise review.
2. Permission filtering before generation.
3. Abstention as a product behavior.
4. Retrieved text as untrusted input.
5. Tool calling versus side-effect authorization.
6. Approval gates and audit logs.
7. Evals as deployment gates.
8. What changes in production: storage, connectors, telemetry.
9. What should not change: security boundaries.
