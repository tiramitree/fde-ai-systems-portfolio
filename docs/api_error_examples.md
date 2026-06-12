# API Error Examples

This page gives copyable local requests for expected JSON error responses. It is local-only: no API keys, external accounts, paid services, private files, generated runtime artifacts, or secret values are required.

Start the demo services from the repository root in one terminal:

```powershell
python -B scripts/dev.py start
```

Keep that command running, then use a second terminal for the examples below. Examples use `curl.exe` so they work in PowerShell. Add `-i` to show the HTTP status and headers.

## Shared Static And JSON Errors

The three app shells share the same static-file and JSON parsing behavior.

### Forbidden Static Traversal

Use `--path-as-is` so curl does not normalize the traversal attempt before it reaches the local server:

```powershell
curl.exe -i --path-as-is http://127.0.0.1:8765/../app.py
```

Expected response:

```http
HTTP/1.0 403 Forbidden
Content-Type: application/json; charset=utf-8
```

```json
{
  "error": "Forbidden"
}
```

The same pattern is covered for all three services by `python -B scripts/dev.py ui-contracts`.

### Missing Static Asset

```powershell
curl.exe -i http://127.0.0.1:8765/missing-static.js
```

Expected response:

```http
HTTP/1.0 404 Not Found
Content-Type: application/json; charset=utf-8
```

```json
{
  "error": "Not found"
}
```

### Invalid JSON Body

```powershell
curl.exe -i -X POST http://127.0.0.1:8765/api/query -H "Content-Type: application/json" --data-raw "{"
```

Expected response:

```http
HTTP/1.0 400 Bad Request
Content-Type: application/json; charset=utf-8
```

```json
{
  "error": "Invalid JSON body"
}
```

### Non-Object JSON Body

```powershell
curl.exe -i -X POST http://127.0.0.1:8765/api/query -H "Content-Type: application/json" --data-raw "[]"
```

Expected response:

```http
HTTP/1.0 400 Bad Request
Content-Type: application/json; charset=utf-8
```

```json
{
  "error": "JSON body must be an object."
}
```

### Request Body Too Large

The default local limit is 1 MiB. This example intentionally sends a larger body:

```powershell
$body = '{"payload":"' + ('x' * 1200000) + '"}'
curl.exe -i -X POST http://127.0.0.1:8765/api/query -H "Content-Type: application/json" --data-raw $body
```

Expected response:

```http
HTTP/1.0 413 Request Entity Too Large
Content-Type: application/json; charset=utf-8
```

```json
{
  "error": "Request body too large."
}
```

### Rate Limit Exceeded

Request governance is intentionally configurable for local verification. Start one service with a tiny request-count limit:

```powershell
$env:FDE_RATE_LIMIT_REQUESTS_PER_WINDOW = "1"
$env:FDE_RATE_LIMIT_BUDGET_PER_WINDOW = "999"
python -B secure-enterprise-knowledge-copilot/app.py --reset --port 8765
```

Then send two governed API requests from another terminal:

```powershell
curl.exe -i http://127.0.0.1:8765/api/health -H "X-Request-ID: review-check-1234"
curl.exe -i http://127.0.0.1:8765/api/health -H "X-Request-ID: review-check-5678"
```

Expected response for the second request:

```http
HTTP/1.0 429 Too Many Requests
Content-Type: application/json; charset=utf-8
X-Request-ID: review-check-5678
Retry-After: 60
```

```json
{
  "error": "Rate limit exceeded.",
  "request_id": "review-check-5678",
  "retry_after_seconds": 60
}
```

The same local boundary also emits `X-RateLimit-Remaining` and `X-RateLimit-Budget-Remaining` on API responses. Run `python -B scripts/dev.py request-governance` to verify request ids, request-count limits, budget limits, and 429 headers across all three services.

## Typed API Errors

Typed application errors still return specific user-safe messages. Unexpected server exceptions are handled separately by `python -B scripts/dev.py error-hygiene` and return only:

```json
{
  "error": "Internal server error"
}
```

### Project 1: Unknown User

```powershell
curl.exe -i "http://127.0.0.1:8765/api/documents?user_id=missing-user"
```

Expected response:

```http
HTTP/1.0 404 Not Found
Content-Type: application/json; charset=utf-8
```

```json
{
  "error": "Unknown user_id: missing-user"
}
```

### Project 1: Invalid Integer Query Parameter

```powershell
curl.exe -i "http://127.0.0.1:8765/api/traces?limit=not-a-number"
```

Expected response:

```http
HTTP/1.0 400 Bad Request
Content-Type: application/json; charset=utf-8
```

```json
{
  "error": "Invalid integer query parameter: limit"
}
```

### Project 2: Non-Supervisor Approval

```powershell
curl.exe -i -X POST http://127.0.0.1:8770/api/approval/approve -H "Content-Type: application/json" -d '{"approval_id":"apr-0001","approver_id":"ivy"}'
```

Expected response:

```http
HTTP/1.0 403 Forbidden
Content-Type: application/json; charset=utf-8
```

```json
{
  "error": "Only supervisors can approve actions."
}
```

### Project 2: Non-Supervisor Rejection

```powershell
curl.exe -i -X POST http://127.0.0.1:8770/api/approval/reject -H "Content-Type: application/json" -d '{"approval_id":"apr-0001","reviewer_id":"ivy","reason":"Not my queue."}'
```

Expected response:

```http
HTTP/1.0 403 Forbidden
Content-Type: application/json; charset=utf-8
```

```json
{
  "error": "Only supervisors can reject actions."
}
```

### Project 2: Non-Supervisor Expiry

```powershell
curl.exe -i -X POST http://127.0.0.1:8770/api/approval/expire -H "Content-Type: application/json" -d '{"approval_id":"apr-0001","operator_id":"ivy","reason":"Trying to close stale work."}'
```

Expected response:

```http
HTTP/1.0 403 Forbidden
Content-Type: application/json; charset=utf-8
```

```json
{
  "error": "Only supervisors can expire actions."
}
```

### Project 3: Unknown Incident

```powershell
curl.exe -i -X POST http://127.0.0.1:8780/api/triage -H "Content-Type: application/json" -d '{"user_id":"maya","release_id":"rel-2026-06-01","incident_id":"missing-incident"}'
```

Expected response:

```http
HTTP/1.0 404 Not Found
Content-Type: application/json; charset=utf-8
```

```json
{
  "error": "Unknown incident_id: missing-incident"
}
```

## Verification Commands

These gates keep the examples aligned with the app shells, API docs, and error hygiene contract:

```powershell
python -B scripts/dev.py api-docs
python -B scripts/dev.py error-hygiene
python -B scripts/dev.py request-body-limits
python -B scripts/dev.py ui-contracts
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

Do not use real user data, local machine paths, tokens, or external service identifiers when adding new error examples.
