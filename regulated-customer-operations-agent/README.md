# Regulated Customer Operations Agent

Governed product-recall operations agent reference system for controlled workflow automation.

The project shows how an AI system can safely participate in a business workflow where some actions have external side effects. The agent may investigate, cite policy, create internal records, draft a seller notice, and schedule follow-up, but it cannot send notices or escalate cases without supervisor approval.

## What It Demonstrates

- Tool calling over case, policy, listing, seller, and product data.
- Policy-grounded reasoning with citations.
- Human approval queue for side-effect actions.
- Governed tool registry with approval, dry-run, and credential-scope metadata.
- Sanitized dry-run previews before side effects execute.
- Approval rejection and expiry paths that close side effects without dispatch.
- Direct side-effect blocking.
- Idempotent approval requests.
- Sanitized workflow-run checkpoints for approval, retry, execution, and dead-letter states.
- Trace logging for routing and tool calls.
- Audit logging for decisions and business actions.
- Golden eval gate for unsafe-action regression testing.

## Run Locally

```powershell
cd regulated-customer-operations-agent
python -B app.py --reset --port 8770
```

Open:

```text
http://127.0.0.1:8770
```

Run evals:

```powershell
python -B scripts\run_eval.py
```

## Demo Users

- `ivy`: investigator. Can investigate and request approvals.
- `sam`: supervisor. Can approve side-effect actions.

## Demo Flow

1. Run investigation for Market Blue / RX-900.
2. Show tool calls: policy search, listing search, violation creation, notice draft, follow-up scheduling.
3. Show that `send_notice` is blocked as a direct side effect.
4. Show approval request in the queue, including dry-run preview, owner, expiry, and payload hash evidence.
5. Approve as supervisor, or reject/expire the approval to prove no side effect executes.
6. Show audit and trace records.
7. Run evals and API contracts.

## FDE Positioning

This is not a generic multi-agent demo. It is scoped around a realistic regulated workflow:

- What tools can the agent call?
- Which actions require approval, dry-run preview, owner review, and expiry?
- How do we prove the model did not send external communication directly?
- How do we debug a failed route or unsafe action?
- How do we regression-test governance behavior?

## Production Upgrade Path

1. Replace local store with PostgreSQL.
2. Replace deterministic router with OpenAI Responses API / Agents SDK.
3. Replace the local tool registry with policy-as-code permissions and scoped external credentials.
4. Replace local workflow checkpoints with durable database-backed workflow state.
5. Add OpenTelemetry traces.
6. Add Docker Compose.
7. Add real connectors for CRM, ticketing, email, and calendar.

## Optional OpenAI Responses API Router

Default mode is local and deterministic.

```powershell
$env:OPENAI_API_KEY="..."
$env:OPENAI_MODEL="gpt-5.2"
$env:OPS_AGENT_MODEL_ROUTER="openai"
python -B app.py --reset --port 8770
```

The model may classify intent, but tool permissions and approval gates remain enforced in application code.

