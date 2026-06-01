# Contributing

This repository is designed as a practical reference for building enterprise AI applications with governance, evals, traces, and demo-ready workflows.

## Good Contributions

- Add realistic enterprise failure cases.
- Improve eval coverage.
- Add production adapters without weakening local deterministic demos.
- Improve security controls around prompt injection, permission filtering, approval gates, or audit logs.
- Add docs that explain tradeoffs clearly.

## Contribution Rules

- Keep both projects runnable with only Python standard library unless the change is behind an optional adapter.
- Do not make OpenAI API calls required for the basic demo.
- Do not move safety enforcement into model prompts only.
- Do not request, print, upload, or depend on secrets, local files, private user data, or account credentials.
- Do not hide eval failures, CI failures, generated artifacts, or network side effects.
- Add or update eval cases for behavior changes.
- Preserve the portfolio-level commands:

```powershell
python -B scripts/dev.py assets
python -B scripts/dev.py architecture
python -B scripts/dev.py claims
python -B scripts/dev.py dependency-surface
python -B scripts/dev.py contracts
python -B scripts/dev.py frontend
python -B scripts/dev.py health
python -B scripts/dev.py evals
python -B scripts/dev.py eval-csv
python -B scripts/dev.py github-launch-setup
python -B scripts/dev.py github-readiness
python -B scripts/dev.py governance
python -B scripts/dev.py model-gateway-safety
python -B scripts/dev.py otel-traces
python -B scripts/dev.py pr-triage
python -B scripts/dev.py readiness-report
python -B scripts/dev.py replay
python -B scripts/dev.py smoke
python -B scripts/dev.py report
python -B scripts/dev.py safety
python -B scripts/dev.py ui-contracts
python -B scripts/dev.py workflow-security
python -B scripts/dev.py verify
```

## Development Flow

1. Start both services.
2. Run health checks.
3. Run evals.
4. Run smoke tests.
5. Run the public safety scan.
6. Run the dependency-surface check.
7. Run the architecture boundary check.
8. Run the workflow security check.
9. Run the model gateway safety check.
10. Run the frontend integrity check.
11. Run the runtime UI contract check.
12. Update docs and demo report if behavior changed.

## Pull Request Checklist

- [ ] The change has a clear business or engineering purpose.
- [ ] Evals pass.
- [ ] Smoke tests pass.
- [ ] Public safety scan passes.
- [ ] Dependency-surface check passes.
- [ ] Architecture boundary check passes.
- [ ] Workflow security check passes.
- [ ] Model gateway safety check passes.
- [ ] Frontend integrity check passes.
- [ ] Runtime UI contract check passes.
- [ ] Security or governance behavior is not weakened.
- [ ] README or docs are updated if the user-facing workflow changed.

See [Maintainer Review Policy](docs/maintainer_review_policy.md) for how reviews and external PRs are triaged.
