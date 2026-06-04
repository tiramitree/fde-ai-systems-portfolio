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
python -B scripts/dev.py ui-contracts
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

Do not use real user data, local machine paths, tokens, or external service identifiers when adding new error examples.
