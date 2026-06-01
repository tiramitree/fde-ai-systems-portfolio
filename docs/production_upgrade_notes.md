# Production Upgrade Notes

## Why The Current Version Is Structured This Way

The local portfolio uses dependency-free Python and static frontend assets so the demos run reliably on the current machine. The core FDE behavior is implemented now:

- permissions before retrieval answer generation
- citations and abstention
- prompt-injection handling
- tool calling
- side-effect approval gates
- audit and trace records
- golden eval gates

Production hardening should upgrade infrastructure without changing these core control boundaries.

## OpenAI Integration

Optional OpenAI Responses API gateways are implemented:

- Project 1: `COPILOT_MODEL_PROVIDER=openai`
- Project 2: `OPS_AGENT_MODEL_ROUTER=openai`

Runtime controls:

- `OPENAI_MODEL=gpt-5.2`
- `OPENAI_REASONING_EFFORT=none|low|medium|high|xhigh`
- `OPENAI_TEXT_VERBOSITY=low|medium|high`

See `docs/model_runtime_configuration.md` for the current model selection rationale.

References:

- Responses API: https://platform.openai.com/docs/api-reference/responses
- Structured Outputs: https://platform.openai.com/docs/guides/structured-outputs?api-mode=responses
- Agents: https://platform.openai.com/docs/guides/agents
- Agent Evals: https://platform.openai.com/docs/guides/agent-evals
- Trace Grading: https://platform.openai.com/docs/guides/trace-grading

The model should not enforce security by itself.

Project 1 still performs:

- tenant and role filtering before generation
- unsafe retrieved-content removal before generation
- citation and abstention decisions in application logic

Project 2 still performs:

- tool permission checks in application logic
- approval gate enforcement in application logic
- side-effect execution only after supervisor approval

## Recommended Production Architecture

```text
Next.js frontend
  -> API gateway
  -> FastAPI services
  -> PostgreSQL
  -> pgvector / search backend
  -> Redis worker queue
  -> OpenAI Responses API / Agents SDK
  -> OpenTelemetry trace backend
  -> CI eval gate
```

## Project 1 Upgrade Path

1. Add file upload.
2. Add document parser pipeline.
3. Add embedding model and vector retrieval.
4. Add BM25 + vector hybrid ranking.
5. Add reranker.
6. Add PostgreSQL row-level security.
7. Add eval cases from real failure logs.

## Project 2 Upgrade Path

1. Replace deterministic routing with Responses API or Agents SDK planning.
2. Keep side-effect tools behind deterministic approval middleware.
3. Add external connectors for CRM/ticketing/email/calendar.
4. Add workflow state machine.
5. Add idempotency and retry policies per connector.
6. Add trace grading for routing, tool choice, and approval compliance.

## Deployment Decision Gate

Do not deploy a change unless:

- health check passes
- all evals pass or approved exceptions are documented
- unsafe leak/direct-side-effect failures remain zero
- trace/audit schema compatibility is preserved
- demo script still works end to end
