# Interview Talking Points

## One-Minute Pitch

I built a governed customer operations agent for product-recall compliance. It investigates active recalled-product listings, cites policy, creates internal violations, drafts seller notices, and schedules follow-ups. It cannot send external notices or escalate cases directly; those actions go through a supervisor approval queue and are audited.

## Why This Is FDE-Relevant

Forward-deployed AI work often means connecting a model to real business systems. The risk is not just wrong text. The risk is the model taking an unsafe action. This project demonstrates tool permissions, approval gates, auditability, idempotency, and evals for agent workflows.

## Core Tradeoff

The current MVP uses deterministic routing so governance behavior is reproducible. In production, I would move reasoning to GPT-5.5 through Responses API or Agents SDK, but keep the approval and permission checks outside the model as deterministic application logic.

## Failure Modes

- Incorrect case metadata could route the agent to the wrong listing.
- Weak policy retrieval could cite the wrong enforcement rule.
- Approval idempotency bugs could create duplicate notices.
- A model-only approval policy would be unsafe; approval enforcement must live in the application layer.
- Eval cases must include adversarial bypass attempts, not just happy paths.

