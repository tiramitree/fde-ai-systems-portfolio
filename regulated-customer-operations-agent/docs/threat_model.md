# Threat Model

## Assets

- Case data.
- Seller contact workflow.
- Violation records.
- Approval queue.
- Audit and trace history.

## Main Risks

1. Agent sends seller notice without approval.
2. Agent escalates case without approval.
3. User prompts the agent to bypass logging.
4. Duplicate tool execution sends duplicate notices.
5. Agent cites policy incorrectly.

## Current Controls

- Direct side-effect blocking.
- Human approval queue.
- Supervisor-only approval endpoint.
- Idempotency key for approval requests.
- Audit events for violation creation, approval request, notice send, and blocked bypass.
- Eval cases for bypass attempts and side-effect prevention.

## Production Controls To Add

- Auth provider integration.
- Policy-as-code permission engine.
- Immutable append-only audit storage.
- Connector-specific rate limits and retries.
- PII redaction for traces.
- Trace grading with model-assisted review.

