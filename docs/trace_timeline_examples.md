# Trace Timeline Examples

This page gives local, copyable timelines for tracing one canonical flow per project from request to persisted evidence. The examples use only fictional seed data and local services. Do not use real user data, local machine paths, tokens, external service identifiers, or generated runtime artifacts when adding new examples.

Start the demo services from the repository root in one terminal:

```powershell
python -B scripts/dev.py start
```

Keep that command running, then use a second terminal for the requests below. Examples use `curl.exe` so they work in PowerShell.

## Project 1: Finance-Access Abstention

Goal: prove an employee cannot retrieve confidential finance evidence, and that the refusal can be followed through trace and audit records.

1. Send the unauthorized finance question as Alice:

```powershell
curl.exe -s -X POST http://127.0.0.1:8765/api/query -H "Content-Type: application/json" -d '{"user_id":"alice","question":"What is the finance retention plan?"}' | python -m json.tool
```

2. In the response, copy `trace_id` and confirm these fields:

```text
abstain_reason: no_accessible_grounded_evidence
permission_blocked_count: greater than 0
citations: does not include finance-retention-plan-2026
```

3. Inspect the persisted trace list and find the object whose `id` matches the copied `trace_id`:

```powershell
curl.exe -s "http://127.0.0.1:8765/api/traces?limit=20" | python -m json.tool
```

4. Inspect linked audit events and find an event whose `details.trace_id` matches the same `trace_id`:

```powershell
curl.exe -s "http://127.0.0.1:8765/api/audit?limit=50" | python -m json.tool
```

Timeline:

```text
request /api/query
  -> response trace_id
  -> trace payload.retrieval.permission_blocked_count
  -> trace payload.output.abstain_reason
  -> audit action query_answered with details.trace_id
```

Protected by:

```powershell
python -B scripts/dev.py observability
python -B scripts/dev.py smoke
python -B scripts/dev.py claims
```

## Project 2: Case-1001 Approval

Goal: prove a governed agent can investigate `case-1001`, create internal records, draft a side effect, block direct execution, and require supervisor approval before sending a notice.

1. Run the canonical investigation:

```powershell
curl.exe -s -X POST http://127.0.0.1:8770/api/agent -H "Content-Type: application/json" -d '{"user_id":"ivy","case_id":"case-1001","message":"Check whether Market Blue still has an active listing for the recalled RX-900 product."}' | python -m json.tool
```

2. In the response, copy `trace_id` and the first `approvals[].id`. In reset state the approval id is usually `apr-0001`. Confirm these fields:

```text
intent: investigate_listing
tool_calls: includes create_violation, draft_seller_notice, schedule_followup
approvals[].action_type: send_notice
blocked_actions: includes a blocked send_notice side effect
model_router: local
```

3. Inspect the approval queue:

```powershell
curl.exe -s http://127.0.0.1:8770/api/approvals | python -m json.tool
```

4. Approve the pending notice as supervisor `sam`:

```powershell
curl.exe -s -X POST http://127.0.0.1:8770/api/approval/approve -H "Content-Type: application/json" -d '{"approval_id":"apr-0001","approver_id":"sam"}' | python -m json.tool
```

5. Inspect traces and audit events:

```powershell
curl.exe -s "http://127.0.0.1:8770/api/traces?limit=20" | python -m json.tool
curl.exe -s "http://127.0.0.1:8770/api/audit?limit=50" | python -m json.tool
```

Timeline:

```text
request /api/agent
  -> response trace_id and approvals[].id
  -> trace result.tool_calls and result.blocked_actions
  -> approval queue record with status pending
  -> supervisor /api/approval/approve
  -> approval queue record with status approved
  -> audit actions approval_requested, agent_message_processed, notice_sent
```

Protected by:

```powershell
python -B scripts/dev.py observability
python -B scripts/dev.py smoke
python -B scripts/dev.py claims
```

## Project 3: Unsafe Canary Triage

Goal: prove an unsafe canary incident blocks rollout, links failed eval evidence, and writes trace and audit records that explain the release decision.

1. Triage the unsafe canary incident:

```powershell
curl.exe -s -X POST http://127.0.0.1:8780/api/triage -H "Content-Type: application/json" -d '{"user_id":"maya","release_id":"rel-2026-06-01","incident_id":"inc-2026-014"}' | python -m json.tool
```

2. In the response, copy `trace_id` and confirm these fields:

```text
decision.recommendation: block_release
decision.release_blocked: true
evidence.eval_run_id: release-eval-2026-06-01
evidence.linked_eval_case_ids: includes rel-eval-003-employee-finance-abstain and rel-eval-004-citation-required
failed_evals: contains failed release eval cases
remediation_steps: contains rollout-blocking follow-up work
```

3. Inspect the trace list and find the object whose `id` matches the copied `trace_id`:

```powershell
curl.exe -s "http://127.0.0.1:8780/api/traces?limit=20" | python -m json.tool
```

4. Inspect audit events and find `incident_triaged` with `details.trace_id` equal to the copied `trace_id`:

```powershell
curl.exe -s "http://127.0.0.1:8780/api/audit?limit=50" | python -m json.tool
```

Timeline:

```text
request /api/triage
  -> response trace_id
  -> decision.recommendation block_release
  -> failed eval cases linked through evidence.linked_eval_case_ids
  -> trace result.release_blocked true
  -> audit action incident_triaged with details.trace_id
```

Protected by:

```powershell
python -B scripts/dev.py observability
python -B scripts/dev.py smoke
python -B scripts/dev.py claims
```

## Verification Commands

Run these before changing trace, audit, approval, eval, or release-decision behavior:

```powershell
python -B scripts/dev.py observability
python -B scripts/dev.py smoke
python -B scripts/dev.py claims
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

Use `docs/api_request_cookbook.md` for the shortest request path and `docs/observability_integrity.md` for the gate-level evidence contract.
