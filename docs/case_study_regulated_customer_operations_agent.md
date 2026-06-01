# Case Study: Regulated Customer Operations Agent

## Problem

Operational teams often need to process repetitive, high-risk workflows. In this example, a compliance investigator must check whether a seller is still listing a recalled product.

A naive agent is unsafe because it might:

- send external notices without approval
- escalate a case incorrectly
- cite the wrong policy
- duplicate side-effect actions
- hide unsafe instructions inside a chat flow

## Design Goal

Build an agent that can investigate, draft, and prepare actions, but cannot execute external side effects without deterministic approval controls.

## Architecture

```text
User request
  -> classify intent
  -> detect bypass attempts
  -> search policy
  -> search listings
  -> create internal violation
  -> draft seller notice
  -> schedule follow-up
  -> create approval request
  -> supervisor approval
  -> execute side effect
  -> write trace and audit
```

## Key Product Behaviors

- Ivy can investigate a recalled product case.
- The system finds active listing `lst-1001`.
- The agent creates an internal violation.
- The agent drafts a seller notice.
- The agent schedules follow-up.
- The agent creates an approval request.
- The notice is not sent until Sam, a supervisor, approves it.
- Bypass prompts are refused and audited.

## Why This Is Not A Toy Agent

Toy agent demos focus on autonomous tool use.

This project focuses on governed tool use:

- direct side effects are blocked
- approval queue is required
- supervisor-only approval endpoint exists
- idempotency prevents duplicate approvals
- audit and trace records are part of the workflow
- evals explicitly test unsafe-action prevention

## Evaluation Strategy

The eval suite checks:

- correct investigation intent
- approval required for notice sending
- approval required for escalation
- bypass prompt refusal
- no direct side-effect tool calls

Latest verified result:

```text
8/8 evals passed
unsafe_direct_side_effect_failures = 0
```

## Hard Interview Answer

If asked why not let the model decide whether to send the notice:

> The model can recommend, classify, and draft, but approval enforcement must be deterministic application logic. External side effects need auditability, consistency, and policy enforcement that do not depend on prompt obedience.

## Production Upgrade

Replace local mocks with:

- CRM connector
- ticketing connector
- email connector
- workflow state machine
- PostgreSQL audit/event log
- policy-as-code authorization
- OpenAI Agents SDK or Responses API planner
- trace grading and red-team evals
