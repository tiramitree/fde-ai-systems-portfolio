# Architecture

```text
Static HTML/JS UI
  -> Python HTTP API
    -> JSON runtime state
    -> agent.py: intent classification and orchestration
    -> tools.py: policy search, listing search, violation, notice draft, approval, follow-up
    -> evals.py: governance regression suite
```

## Tool Governance

Internal actions:

- `search_recall_policy`
- `get_case`
- `search_listings`
- `create_violation`
- `draft_seller_notice`
- `schedule_followup`

Side-effect actions:

- `send_notice`
- `escalate_case`

Side-effect actions are not executed directly by the investigator. The agent creates an approval request with an idempotency key. A supervisor must approve before the side effect is applied.

## Production Version

```text
Next.js case workspace
  -> API gateway
  -> FastAPI agent service
  -> OpenAI Responses API / Agents SDK
  -> Tool registry and policy engine
  -> PostgreSQL workflow state
  -> CRM / ticketing / email connectors
  -> Trace and eval service
```

