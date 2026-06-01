# API Contracts

Run:

```bash
python -B scripts/dev.py contracts
python -B scripts/dev.py api-docs
```

The demos expose small HTTP APIs so the browser remains a thin client over explicit backend boundaries. `contracts` starts isolated services and verifies response shapes at runtime. `api-docs` verifies this document stays aligned with the source routes and public evidence map.

## Shared Rules

- Responses are JSON.
- Errors use `{"error": "message"}` with an HTTP status code.
- Runtime route contracts are checked separately by `python -B scripts/dev.py ui-contracts`.
- The model is not the API authorization boundary; permission and approval checks happen in application code before responses are returned.

## Secure Enterprise Knowledge Copilot

Source:

- `secure-enterprise-knowledge-copilot/src/copilot/api.py`
- Runtime gate: `scripts/check_api_contracts.py`

### Routes

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/health` | Service health and app name. |
| GET | `/api/users` | Demo users with `id`, `name`, `role`, and `tenant_id`. |
| GET | `/api/documents?user_id=alice` | Visible document metadata for the requester. Document `body` is never returned. |
| GET | `/api/traces?limit=25` | Recent trace records. |
| GET | `/api/audit?limit=50` | Recent audit events. |
| GET | `/api/eval/latest` | Latest eval run record. |
| POST | `/api/query` | Permission-aware answer generation with citations or abstention. |
| POST | `/api/eval/run` | Run the project eval suite. |

### Query Response Shape

`POST /api/query` returns:

- `trace_id`
- `user`
- `question`
- `answer`
- `citations`
- `confidence`
- `missing_evidence`
- `abstain_reason`
- `security_events`
- `model_provider`
- `openai_gateway_enabled`
- `retrieved`
- `permission_blocked_count`
- `latency_ms`

Security contract:

- unauthorized evidence is filtered before answer generation
- retrieved prompt-injection markers become security events
- unsupported or inaccessible questions abstain
- inaccessible document bodies are not returned in `/api/documents`
- document body is never returned

## Regulated Customer Operations Agent

Source:

- `regulated-customer-operations-agent/src/ops_agent/api.py`
- Runtime gate: `scripts/check_api_contracts.py`

### Routes

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/health` | Service health and app name. |
| GET | `/api/users` | Demo users with `id`, `name`, and `role`. |
| GET | `/api/cases` | Demo operational cases. |
| GET | `/api/approvals` | Approval queue state. |
| GET | `/api/traces?limit=25` | Recent trace records. |
| GET | `/api/audit?limit=50` | Recent audit events. |
| GET | `/api/eval/latest` | Latest eval run record. |
| POST | `/api/agent` | Process an investigator/supervisor workflow message. |
| POST | `/api/approval/approve` | Supervisor-only approval execution. |
| POST | `/api/eval/run` | Reset state and run the project eval suite. |

### Agent Response Shape

`POST /api/agent` returns:

- `trace_id`
- `intent`
- `response`
- `tool_calls`
- `approvals`
- `blocked_actions`
- `cited_policies`
- `outputs`
- `case`
- `model_router`

Security contract:

- investigator side effects create approval requests instead of executing directly
- non-supervisors receive `403` when approving actions
- supervisor approval is idempotent
- bypass instructions create blocked-action evidence instead of side effects
- `model_router` reports the actual routing source for the intent classification path, not just whether OpenAI mode was configured

## Interview Framing

Use this answer:

```text
The browser talks to a small documented API surface. I verify the response shapes at runtime with `contracts`, and I verify the public API documentation with `api-docs` so a reviewer can map UI behavior to backend responsibilities. The important boundary is that permissions and side effects are enforced before the JSON response, not by trusting model text.
```
