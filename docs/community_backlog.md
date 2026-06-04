# Community Backlog

This backlog is designed for public GitHub issues after launch. It keeps the repository open-source friendly by pointing contributors toward real improvements without weakening the core demo.

## Good First Issues

1. Add a narrated demo video using the walkthrough GIF as the storyboard.
2. Add compact docs for issue-to-PR handoff flow.
3. Add compact release attachment verification examples.
4. Add compact eval CSV troubleshooting examples.
5. Add compact branch protection verification examples.

## Intermediate Issues

1. Add a hybrid BM25 + vector retrieval path behind a feature flag.
2. Add live OTLP HTTP export to an OpenTelemetry Collector.
3. Add per-case eval reports with failure diffs.
4. Add Docker Compose runtime screenshots after testing on a Docker-enabled machine.
5. Add release automation that uploads `out/demo_replay_artifact.md` and `out/demo_replay_artifact.json` after `python -B scripts/dev.py replay-artifact` passes.

## Advanced Issues

1. Implement PostgreSQL and pgvector storage adapters from the design note.
2. Add connector stubs for Google Drive, Slack, Jira, CRM, email, and calendar.
3. Add model-backed eval grading while keeping deterministic safety assertions.
4. Add a multi-tenant permission model with row-level policy examples.
5. Add a state-machine engine for governed operations workflows.

## Guardrails

Contributions should preserve these invariants:

- Project 1 must not expose inaccessible evidence to the model.
- Project 1 must abstain on unknown or unauthorized questions.
- Project 2 must not execute side-effect tools without application-level authorization.
- Project 2 must preserve supervisor approval behavior.
- Project 3 must block unsafe release rollout when high-risk incidents are linked to failed evals.
- Eval gates must keep unsafe leak, unsafe direct side-effect, and unsafe release approval failures at zero.

## Recently Completed

- Add keyboard-friendly trace navigation for recent trace lists.
- Add copyable scenario-draft import/export snippets for local demos.
- Add a compact diff view for browser-local scenario drafts.
- Add a reduced-motion and focus-visible accessibility pass for all demo UIs.
- Add browser-local light/dark theme controls to all demo UIs.
- Add high-contrast screenshot checks for future visual asset refreshes.
- Add mobile viewport screenshots to the visual asset manifest.
- Add compact visual asset diff summaries for screenshot refreshes.
- Add visual asset refresh troubleshooting notes for browser capture failures.
- Add per-asset captions for the desktop and mobile screenshot gallery.
- Add a README command quick-reference grouped by local run, verification, release, visual assets, GitHub maintenance, and optional environment checks.
- Add a compact glossary for release gates, eval gates, approval gates, trace IDs, audit logs, and abstention.
- Add a README maintainer workflow checklist for reviewing external PRs without running untrusted code first.
- Add a compact README section that maps each project to the smallest useful demo path.
- Add a README command output expectations table for verify, quality, fresh-clone, post-publish, GitHub readiness, and PR triage checks.
- Add a compact README troubleshooting pointer for API rate limits, Docker availability, optional OpenAI mode, and generated local artifacts.
- Add a compact README reviewer checklist for comparing the screenshot gallery with live demo behavior.
- Add a compact README command decision tree for choosing local, release, GitHub, visual asset, and optional environment checks.
- Add a compact README evidence legend for distinguishing smoke, eval, trace, audit, and visual gates.
- Add a compact README contributor route map for docs-only, frontend, backend, eval, visual asset, and GitHub-maintenance changes.
- Add a compact README production-upgrade pointer for FastAPI, PostgreSQL, pgvector, connectors, OpenTelemetry, OpenAI, and Docker paths.
- Add a compact README release-evidence FAQ for quality, fresh-clone, post-publish, and GitHub readiness warnings.
- Add compact per-project risk badges for permissions, approvals, evals, traces, and release blocking.
- Add a compact README operational runbook index for retrieval, approval, and release-blocking scenarios.
- Add a compact README evidence freshness checklist for screenshots, eval summaries, and published status.
- Add a compact README reviewer handoff checklist for local, remote, visual, and GitHub account-level checks.
- Add compact per-project architecture cards to the README.
- Add shareable demo-state reset presets.
- Add a compact README demo recording checklist pointer for maintainers.
- Add a compact README launch-channel checklist pointer for maintainers.
- Add a compact README contribution safety summary pointer.
- Add a compact README release artifact attachment pointer.
- Add a compact README optional-environment evidence pointer.
- Add a compact README connector roadmap pointer.
- Add a compact README eval regression report pointer.
- Add a compact README storage adapter evidence pointer.
- Add a compact README red-team eval expansion pointer.
- Add a compact README OpenTelemetry backend pointer.
- Add a compact README Docker runtime evidence pointer.
- Add a compact README dependency surface evidence pointer.
- Add a compact README API contract evidence pointer.
- Add a compact README error hygiene evidence pointer.
- Add a compact README model gateway safety evidence pointer.
- Add a compact README PR triage evidence pointer.
- Add a compact README threat model evidence pointer.
- Add a compact README workflow security evidence pointer.
- Add a compact README governance evidence pointer.
- Add a compact README launch asset evidence pointer.
- Add a compact README reviewer handoff evidence pointer.
- Add a compact README post-publish evidence pointer.
- Add a compact README GitHub readiness evidence pointer.
- Add a compact README release page evidence pointer.
- Add an API request cookbook for the canonical demo paths.
- Add a contributor code-tour page for API, service, storage, and frontend boundaries.
- Add an eval authoring guide for safe retrieval, approval, and release-blocking cases.
- Add seed-data extension examples for one document, one operations case, and one incident.
- Add local API error examples for 403, 404, and invalid JSON responses.
- Add a trace timeline explainer for canonical flows.
- Add contributor-local troubleshooting examples for failed eval gates.
- Add a small glossary for seed, runtime, eval, replay, and trace artifacts.
- Add a command-output troubleshooting map for the most common failing gates.
- Add a local demo reset troubleshooting guide for stale runtime state.
- Add a concise data-flow map for each service's checked-in seed fixtures.
- Add a contributor onboarding checklist for the first local pull request.
- Add docs-only pull request review examples for useful, low-signal, and unsafe documentation changes.
- Add docs-only review comments for common PR outcomes.
- Add a README-to-docs navigation audit for release-facing docs.
- Add compact examples for README navigation drift fixes.
- Add OpenTelemetry collector handoff troubleshooting notes.
- Add optional OpenAI live-mode troubleshooting notes.
- Add a Docker runtime evidence collection checklist.
- Add compact Docker runtime failure examples.
