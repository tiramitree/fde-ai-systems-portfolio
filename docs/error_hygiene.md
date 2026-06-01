# Error Hygiene

Public demos should fail safely. Unexpected backend exceptions must not leak stack traces, local paths, secret-like strings, source file names, or internal implementation details into browser-visible JSON responses.

Run the error hygiene gate with:

```bash
python -B scripts/dev.py error-hygiene
```

## What It Verifies

The gate imports both local app shells, replaces each API object with a test double that raises an exception containing local-path and secret-like markers, starts each HTTP handler on an isolated port, and checks both `GET` and `POST` API paths.

It fails if:

- either `app.py` renders `str(exc)` for unexpected exceptions
- either `app.py` imports or renders traceback output
- either app lacks the generic `"Internal server error"` response
- an unexpected exception returns a non-500 status
- an unexpected exception returns a non-JSON response
- the response body contains local paths, private machine markers, secret-like markers, or the raw exception message

Expected user-visible payload:

```json
{
  "error": "Internal server error"
}
```

## Boundary

Typed application errors still return specific user-safe messages through `ApiError`, such as `Not found`, `Forbidden`, or validation errors. Only unexpected server exceptions are generalized.

This keeps the demo useful for users while avoiding accidental leakage during interviews, public PR testing, or future refactors.
