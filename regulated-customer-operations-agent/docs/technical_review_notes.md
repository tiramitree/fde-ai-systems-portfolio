# Technical Review Notes

## System Summary

The governed operations agent supports product-recall compliance workflows. It investigates active recalled-product listings, cites policy, creates internal violations, drafts seller notices, and schedules follow-ups. It cannot send external notices or escalate cases directly; those actions go through a supervisor approval queue and are audited.

## Why It Matters

Model-facing workflow automation needs more than correct text. The critical risk is unsafe side effects. This project demonstrates tool permissions, approval gates, auditability, idempotency, and evals for agent workflows.

## Core Tradeoff

The MVP uses deterministic routing so governance behavior is reproducible. A production model router can use OpenAI Responses API or Agents SDK, while approval and permission checks remain deterministic application logic outside the model.

## Failure Modes

- Incorrect case metadata can route the agent to the wrong listing.
- Weak policy retrieval can cite the wrong enforcement rule.
- Approval idempotency bugs can create duplicate notices.
- Model-only approval policy is unsafe; approval enforcement must live in the application layer.
- Eval cases must include adversarial bypass attempts, not just happy paths.
