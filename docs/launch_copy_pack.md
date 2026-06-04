# Launch Copy Pack

Use this after the GitHub repository is public and GitHub Actions is green. Before posting, run `python -B scripts/dev.py launch-assets` to check that the launch copy remains complete and does not claim unfinished external blockers. After posting, use `docs/launch_feedback_collection_examples.md` before recording comments, private messages, analytics, stars, or forks as feedback evidence.

## One-Line Pitch

```text
Three local-first enterprise AI reference systems showing secure RAG, governed agents, AI release reliability, evals, traces, audit logs, and approval gates.
```

## Short Post

```text
Open-source reference systems for enterprise AI controls:

- Secure Enterprise Knowledge Copilot: permission-aware RAG with citations, abstention, prompt-injection handling, traces, audit logs, and evals.
- Regulated Customer Operations Agent: governed tool-calling workflow with approval queues, side-effect blocking, supervisor approval, traces, audit logs, and unsafe-action evals.
- AI Reliability Incident Console: canary incident triage, eval regression evidence, rollout blocking, remediation plans, traces, and audit logs.

The systems run locally without paid APIs, with optional OpenAI Responses API integration points and a production upgrade path.

The key design principle: the model is not the security boundary. Permissions, side-effect authorization, rollout decisions, audit, traces, and evals live in application code.
```

## LinkedIn Post

```text
Most AI app demos stop at chat.

Enterprise deployments need the controls around the model:

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

3. AI Reliability Incident Console
   - canary incident triage
   - eval regression evidence
   - rollout blocking
   - remediation plans
   - traces and audit logs

All three run locally without paid APIs. Optional model-backed paths are configurable, but the important controls stay outside the model.

The design principle is simple: the model is not the security boundary.

Repo: <repo-url>
```

## X / Twitter Thread

```text
1/ Local-first enterprise AI reference systems.

Not another chatbot template:
- secure RAG
- governed agents
- AI release reliability
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

4/ Project 3: AI Reliability Incident Console.

It links canary incidents to failed eval cases, blocks unsafe rollout, keeps latency-only incidents monitor-only, and creates trace/audit evidence for release decisions.

5/ The model is not the security boundary.

Permissions, side-effect authorization, rollout decisions, audit, traces, and evals stay in application code.

6/ The systems run locally without paid APIs and include optional OpenAI Responses API integration points.

Repo: <repo-url>
```

## Hacker News Show HN

Title:

```text
Show HN: Local-first enterprise AI systems with secure RAG, governed agents, and release gates
```

Body:

```text
This is a small local-first reference repository for enterprise AI control patterns.

It contains three runnable systems:

- Secure Enterprise Knowledge Copilot: permission-aware RAG with citations, abstention, prompt-injection handling, traces, audit logs, and evals.
- Regulated Customer Operations Agent: governed tool-calling workflow with approval queues, side-effect blocking, supervisor approval, traces, audit logs, and unsafe-action evals.
- AI Reliability Incident Console: canary incident triage, eval regression evidence, rollout blocking, remediation plans, traces, and audit logs.

The repo is intentionally dependency-light so reviewers can run it locally without paid APIs. Optional OpenAI Responses API integration points are included, but security, side-effect, and release boundaries stay in application code.

The core idea is: the model is not the security boundary.

Feedback on the eval design, permission boundary, governed-agent workflow, and release reliability gate would be especially useful.
```

## Reddit / Community Post

```text
Local-first enterprise AI reference systems focused on the controls around LLM apps:

- secure RAG with role-aware retrieval
- citations and abstention
- retrieved-content prompt-injection handling
- governed tool-calling agent
- approval gates for side effects
- AI release incident triage
- rollout blocking from eval regressions
- traces and audit logs
- eval and smoke-test gates

This is intentionally not a production platform. It is a runnable reference implementation for enterprise AI/FDE control patterns and early AI product pilots.

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
7. Release blocking from eval regressions.
8. Evals as deployment gates.
9. What changes in production: storage, connectors, telemetry.
10. What should not change: security boundaries.
