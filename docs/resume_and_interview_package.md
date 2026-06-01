# Resume And Interview Package

## Portfolio Positioning

Target roles:

- Forward Deployed Engineer
- AI Application Engineer
- LLM Application Engineer
- AI Agent Full-stack Engineer
- 大模型应用工程师
- 大模型解决方案工程师

## One-Line Pitch

I build enterprise AI applications that connect models to real business workflows with permissions, citations, tool governance, human approval, audit logs, traces, and eval gates.

## Project 1 Resume Bullet

Built a permission-aware enterprise knowledge copilot with role-based retrieval, citation enforcement, abstention, prompt-injection checks, trace logging, audit events, and eval-gated regression tests using Python, static web UI, and a production upgrade path to GPT-5.5, FastAPI, PostgreSQL/pgvector, and OpenTelemetry.

## Project 2 Resume Bullet

Developed a governed customer operations agent for product-recall compliance workflows, integrating tool calling, policy-grounded decisions, violation creation, seller-notice drafting, human approval queues, direct side-effect blocking, audit logs, traces, and unsafe-action evals.

## Interview Story

The first project proves I can build secure enterprise RAG. The second project proves I can connect an agent to business tools without letting it take unsafe external actions. Together they show the FDE pattern: clarify the workflow, design the system, build the product, instrument traces and evals, and expose the tradeoffs clearly.

## Demo Order

1. Open Project 1 and show Alice vs Morgan permissions.
2. Show Project 1 abstention and prompt-injection handling.
3. Run Project 1 eval gate.
4. Open Project 2 and run the Market Blue investigation.
5. Show approval queue and blocked direct `send_notice`.
6. Approve as supervisor and show audit.
7. Run Project 2 eval gate.

## Key Technical Claims

- Permission checks happen before evidence assembly.
- Retrieved content is treated as data, not instructions.
- Side-effect tools are gated by application logic, not model promises.
- Evals include negative cases and bypass attempts.
- Traces and audit logs are first-class product surfaces, not afterthoughts.

## Production Upgrade Answer

The current local version is dependency-free for reliable demonstration. In production I would replace local stores with PostgreSQL and pgvector, use FastAPI and Next.js, integrate GPT-5.5 through Responses API or Agents SDK, add OpenTelemetry traces, run evals in CI, and connect to enterprise systems such as Drive, Slack, Jira, CRM, email, and calendar through permissioned connectors.
