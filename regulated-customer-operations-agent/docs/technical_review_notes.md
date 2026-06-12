# Technical Review Notes

## System Summary

The governed operations agent supports product-recall compliance workflows. It investigates active recalled-product listings, cites policy, creates internal violations, drafts seller notices, and schedules follow-ups. It cannot send external notices or escalate cases directly; those actions go through a tool registry, sanitized dry-run preview, supervisor approval queue, rejection/expiry path, sanitized workflow-run checkpoint, action-outbox dispatch record with local worker lease evidence, idempotent action-run receipt after approval or retry, and audit log.

## Why It Matters

Model-facing workflow automation needs more than correct text. The critical risk is unsafe side effects. This project demonstrates tool permissions, dry-run previews, approval gates, rejection/expiry handling, auditability, idempotency, and evals for agent workflows.

## Core Tradeoff

The MVP uses deterministic routing so governance behavior is reproducible. A production model router can use OpenAI Responses API or Agents SDK, while approval and permission checks remain deterministic application logic outside the model.

## Failure Modes

- Incorrect case metadata can route the agent to the wrong listing.
- Weak policy retrieval can cite the wrong enforcement rule.
- Approval idempotency bugs can create duplicate notices.
- Missing workflow checkpoints make it hard to explain whether an agent run is waiting for approval, recovered after retry, completed, or dead-lettered.
- Missing durable outbox state makes approval/execution recovery hard after a restart or partial failure.
- Missing retry/dead-letter state hides dispatch failures and leaves operators unable to prove whether an approved action was recovered or abandoned.
- Missing rejection/expiry states can leave stale approvals ambiguous and make it unclear whether a side effect was intentionally closed.
- Missing execution receipts make it hard to prove whether an approved side effect actually ran once.
- Model-only approval policy is unsafe; approval enforcement must live in the application layer.
- Eval cases must include adversarial bypass attempts, not just happy paths.
