# Contributing

This repository is designed as a practical reference for building enterprise AI applications with governance, evals, traces, and demo-ready workflows.

## Good Contributions

- Add realistic enterprise failure cases.
- Improve eval coverage.
- Add production adapters without weakening local deterministic demos.
- Improve security controls around prompt injection, permission filtering, approval gates, or audit logs.
- Add docs that explain tradeoffs clearly.

## Contribution Rules

- Keep all projects runnable with only Python standard library unless the change is behind an optional adapter.
- Do not make OpenAI API calls required for the basic demo.
- Do not move safety enforcement into model prompts only.
- Do not request, print, upload, or depend on secrets, local files, private user data, or account credentials.
- Do not hide eval failures, CI failures, generated artifacts, or network side effects.
- Add or update eval cases for behavior changes.
- Preserve the portfolio-level commands:

```powershell
python -B scripts/dev.py api-docs
python -B scripts/dev.py assets
python -B scripts/dev.py architecture
python -B scripts/dev.py claims
python -B scripts/dev.py container-release
python -B scripts/dev.py dependency-surface
python -B scripts/dev.py contracts
python -B scripts/dev.py error-hygiene
python -B scripts/dev.py frontend
python -B scripts/dev.py health
python -B scripts/dev.py evals
python -B scripts/dev.py eval-csv
python -B scripts/dev.py fresh-clone
python -B scripts/dev.py github-launch-setup
python -B scripts/dev.py github-readiness
python -B scripts/dev.py governance
python -B scripts/dev.py model-gateway-safety
python -B scripts/dev.py observability
python -B scripts/dev.py otel-traces
python -B scripts/dev.py pr-policy
python -B scripts/dev.py pr-triage
python -B scripts/dev.py readiness-report
python -B scripts/dev.py replay
python -B scripts/dev.py replay-artifact
python -B scripts/dev.py scenario-data
python -B scripts/dev.py smoke
python -B scripts/dev.py report
python -B scripts/dev.py safety
python -B scripts/dev.py threat-model
python -B scripts/dev.py ui-contracts
python -B scripts/dev.py visual-assets
python -B scripts/dev.py workflow-security
python -B scripts/dev.py verify
```

## Development Flow

1. Start both services.
2. Run health checks.
3. Run evals.
4. Run smoke tests.
5. Run the public safety scan.
6. Run the container release hygiene check.
7. Run the dependency-surface check.
8. Run the architecture boundary check.
9. Run the workflow security check.
10. Run the model gateway safety check.
11. Run the observability integrity check.
12. Run the scenario data integrity check.
13. Run the error hygiene check.
14. Run the frontend integrity check.
15. Run the threat model check.
16. Run the PR review policy check.
17. Run the runtime UI contract check.
18. Run the visual asset manifest check.
19. Run the API documentation check.
20. Run the replay artifact export before release updates.
21. Run the fresh clone check before broad external sharing or release updates.
22. Update docs and demo report if behavior changed.

## Pull Request Checklist

- [ ] The change has a clear business or engineering purpose.
- [ ] Evals pass.
- [ ] Smoke tests pass.
- [ ] Public safety scan passes.
- [ ] Container release hygiene check passes.
- [ ] Dependency-surface check passes.
- [ ] Architecture boundary check passes.
- [ ] Workflow security check passes.
- [ ] Model gateway safety check passes.
- [ ] Observability integrity check passes.
- [ ] Scenario data integrity check passes.
- [ ] Error hygiene check passes.
- [ ] Frontend integrity check passes.
- [ ] Threat model check passes.
- [ ] PR review policy check passes.
- [ ] Runtime UI contract check passes.
- [ ] Visual asset manifest check passes.
- [ ] API documentation check passes.
- [ ] Replay artifact export passes before release updates.
- [ ] Fresh clone check passes before broad external sharing or release updates.
- [ ] Security or governance behavior is not weakened.
- [ ] README or docs are updated if the user-facing workflow changed.

See [First Pull Request Checklist](docs/first_pull_request_checklist.md) and [Issue To PR Handoff Flow](docs/issue_to_pr_handoff_flow.md) before opening a local PR, and [Maintainer Review Policy](docs/maintainer_review_policy.md) for how reviews and external PRs are triaged.
