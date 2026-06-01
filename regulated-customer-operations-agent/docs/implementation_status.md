# Implementation Status

Date: 2026-06-01

## Current Runnable State

Project path:

```text
regulated-customer-operations-agent
```

Run command:

```powershell
cd regulated-customer-operations-agent
python -B app.py --reset --port 8770
```

Local URL:

```text
http://127.0.0.1:8770
```

Eval command:

```powershell
python -B scripts\run_eval.py
```

## Implemented Capabilities

- Case workspace UI.
- Investigator and supervisor users.
- Policy, product, seller, listing, and case data.
- Agent intent routing.
- Tool calls for policy search, listing search, violation creation, notice draft, follow-up scheduling.
- Approval queue for `send_notice` and `escalate_case`.
- Supervisor-only approval endpoint.
- Direct side-effect blocking.
- Bypass prompt detection.
- Trace and audit logs.
- Golden eval suite.

## Verified Capabilities

- API health endpoint returns OK on port `8770`.
- CLI eval passes 8/8 cases.
- Browser UI loads successfully.
- Investigation flow creates violation, draft notice, follow-up, and approval request.
- `send_notice` is blocked as a direct investigator action.
- Supervisor approval sends the notice after approval.
- UI eval button returns pass rate 1.0 and unsafe direct side-effect failures 0.

Latest verified eval result:

```text
total_cases: 5
passed_cases: 5
pass_rate: 1.0
unsafe_direct_side_effect_failures: 0
```

## Not Yet Production-Grade

- OpenAI Responses API / Agents SDK integration.
- Real external connectors.
- PostgreSQL workflow state.
- Policy-as-code engine.
- PII redaction pipeline.
- Docker Compose.
- Screenshot/demo video package.

