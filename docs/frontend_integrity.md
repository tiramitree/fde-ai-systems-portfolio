# Frontend Integrity

Both demos keep the frontend deliberately simple: first-party HTML, CSS, and ES modules that call backend API routes. There is no build step, CDN, npm dependency, or hidden generated bundle in the local demo path.

## Verified Surface

`python -B scripts/dev.py frontend` checks:

- `web/index.html` exists for both projects.
- the expected page title, stylesheet, and `/js/app.js` module are present.
- required DOM ids exist and are unique.
- form controls used in the demo have labels.
- quick-action buttons are wired through data attributes.
- trace panels expose a copy trace ID command backed by a local clipboard module.
- local ES module imports resolve inside the project `web/js` directory.
- every `byId(...)` target used by JavaScript exists in the HTML.

The full release gate runs the same check through:

```bash
python -B scripts/dev.py verify
```

## Interview Framing

The frontend is intentionally boring in the best sense: it is a thin operational surface over separately testable backend APIs. That keeps the demo inspectable, avoids supply-chain noise, and makes the important product behavior visible: permissions, citations, abstention, traces, audit logs, evals, side-effect blocking, and approvals.
