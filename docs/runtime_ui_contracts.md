# Runtime UI Contracts

The frontend integrity gate checks files. The runtime UI contract gate checks what the running services actually serve over HTTP.

## Verified Surface

`python -B scripts/dev.py ui-contracts` starts all demos on isolated ports and verifies:

- `/` returns the expected HTML shell.
- `/styles.css`, `/js/app.js`, and `/js/api.js` are served with text content types.
- static responses include `Content-Length`.
- static and JSON responses include `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`, and a restrictive local-demo Content Security Policy.
- `/js/traceLinks.js` is served for local trace deep-link behavior.
- missing static files return a JSON 404.
- direct path traversal attempts such as `/../app.py` return 403.

The full release gate runs this check through:

```bash
python -B scripts/dev.py verify
```

## Technical Review Framing

This is not a full production web security posture. It is a local-demo contract that proves the UI is served intentionally: no remote bundle, no accidental source-file exposure, stable content types, and basic browser safety headers.
