# Architecture

```text
Static ES-module UI
  -> api.js: HTTP client
  -> dom.js: safe DOM helpers
  -> renderers.js: UI rendering
  -> app.js: screen orchestration
  -> Python HTTP API
    -> api.py: application API layer
    -> JSON runtime state
    -> agent.py: intent classification and orchestration
    -> tools.py: policy search, listing search, violation, notice draft, tool registry, approval, follow-up
    -> workflows.py: sanitized workflow-run checkpoints
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

The tool registry declares each tool's role boundary, approval requirement, dry-run requirement, side-effect flag, credential scope, and risk level. Side-effect approval requests carry `approval_policy_v1`, owner role, expiry, payload hash, sanitized payload summary, decision-summary metadata, and a `dry_run_preview_v1` record so reviewers can inspect the intended action without receiving raw seller notice bodies or raw escalation reasons.

Each approval request also creates an action-outbox item. The outbox item is the durable dispatch checkpoint for the side effect: it starts as `awaiting_approval`, moves through dispatch when the supervisor approves, and normally ends as `succeeded` with an execution ID. Rejection and expiry close the item as `approval_rejected` or `approval_expired` without execution. Each dispatch attempt records a local worker lease (`lease_id`, `leased_by`, `lease_count`, lease timestamps, and last lease owner) so reviewer-visible evidence can explain who owned a failed or recovered dispatch attempt. Dispatch failures that occur before the side effect is applied move to `retryable_failure` with a sanitized `last_error`, `next_attempt_at`, released lease evidence, and incremented attempt count. Repeated failures move to `dead_lettered` with a dead-letter reason instead of losing approval context. The outbox record keeps payload hashes, dry-run previews, sanitized payload summaries, attempt counts, approval refs, output refs, lease evidence, and status without returning raw seller notice bodies.

Approved side effects write an action-run receipt before the response returns. The receipt records the approval ID, actor IDs, action type, idempotency key, payload hash, sanitized payload summary, output references, status, and result. Replaying the same approval returns the existing execution receipt and outbox item instead of sending a duplicate notice or escalating a case twice. Retrying a `retryable_failure` outbox item uses the same idempotency key and either recovers into a single execution receipt or remains visible as failed/dead-lettered operator evidence.

Workflow runs sit one layer above the action outbox. A workflow run records how a single agent message moved through the governed process: intent classification, tool calls, approval request, waiting state, approval rejection, approval expiry, approved execution, retryable dispatch failure, recovery, or dead-letter. The checkpoint links trace IDs, approval IDs, outbox IDs, and action-run IDs, but returns only message hashes, counts, stages, statuses, and references. It does not return raw user messages, raw seller notice bodies, or raw escalation reasons. This gives reviewers a restart-safe state-machine boundary today while leaving the durable production implementation to a database-backed workflow engine later.

## Production Version

```text
Next.js case workspace
  -> API gateway
  -> FastAPI agent service
  -> OpenAI Responses API / Agents SDK
  -> Tool registry and policy engine
  -> Workflow run checkpoints
  -> Transactional outbox / action-run ledger
  -> PostgreSQL workflow state
  -> CRM / ticketing / email connectors
  -> Trace and eval service
```
