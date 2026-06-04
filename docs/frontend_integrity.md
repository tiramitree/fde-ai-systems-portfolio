# Frontend Integrity

All demos keep the frontend deliberately simple: first-party HTML, CSS, and ES modules that call backend API routes. There is no build step, CDN, npm dependency, or hidden generated bundle in the local demo path.

## Verified Surface

`python -B scripts/dev.py frontend` checks:

- `web/index.html` exists for all projects.
- the expected page title, stylesheet, and `/js/app.js` module are present.
- required DOM ids exist and are unique.
- form controls used in the demo have labels.
- quick-action buttons are wired through data attributes.
- trace panels expose copy trace ID and copy trace link commands backed by a local clipboard module.
- recent trace lists expose local `#trace=` links, selected-trace highlighting, visible focus styling, and keyboard navigation.
- scenario draft panels load read-only seed snapshots, copy/export local JSON drafts, show compact local diffs, and store edited drafts in browser `localStorage`.
- shared accessibility CSS keeps focus-visible rings for buttons, selects, textareas, and trace links, plus a reduced-motion rule for motion-sensitive users.
- local ES module imports resolve inside the project `web/js` directory.
- every `byId(...)` target used by JavaScript exists in the HTML.

The full release gate runs the same check through:

```bash
python -B scripts/dev.py verify
```

## Technical Review Framing

The frontend is intentionally boring in the best sense: it is a thin operational surface over separately testable backend APIs. That keeps the demo inspectable, avoids supply-chain noise, and makes the important product behavior visible: permissions, citations, abstention, traces, audit logs, evals, side-effect blocking, approvals, rollout decisions, and fictional scenario data. Trace links are local URL fragments with keyboard-friendly navigation, scenario drafts are copyable browser-local storage with browser-computed diffs, and focus/reduced-motion rules keep the demos reviewable without adding routing infrastructure or server-side mutation.
