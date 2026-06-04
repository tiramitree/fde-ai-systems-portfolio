# Dependabot And Secret-Scanning Verification Examples

Use this page when reviewing dependency monitoring, GitHub security settings, or secret-alert evidence. Read it with `.github/dependabot.yml`, `docs/supply_chain_security.md`, `docs/post_publish_checklist.md`, `docs/post_publish_warning_examples.md`, `docs/github_repository_settings.md`, and `docs/command_output_troubleshooting_map.md`.

The core rule: checked-in policy files, GitHub account-level security settings, generated alerts, and local safety scans prove different things. Do not claim Dependabot or secret-scanning setup is complete until public/account-level evidence confirms it.

## Expected Evidence Split

Local dependency policy evidence:

```bash
python -B scripts/dev.py dependency-surface
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

Remote repository evidence:

```bash
python -B scripts/dev.py github-readiness
```

Authenticated account-level planning evidence:

```bash
python -B scripts/dev.py github-maintenance
```

`.github/dependabot.yml` proves the desired update surfaces are tracked in source. It does not prove GitHub security features, Dependabot alerts, Dependabot security updates, secret scanning, or push protection are enabled in the repository settings.

## Missing Dependabot Config

Symptom:

- `.github/dependabot.yml` is missing.
- `dependency-surface` reports missing Dependabot coverage.
- GitHub security settings might still exist, but the source policy is absent.

Wrong fix:

- Claim dependency monitoring from GitHub UI settings alone.
- Add a broad package-manager manifest just to make Dependabot active.
- Disable the dependency-surface gate.

Safe fix:

```bash
python -B scripts/dev.py dependency-surface
python -B scripts/dev.py governance
```

Keep the checked-in config narrow: GitHub Actions and the three Dockerfile directories are the current monitored update surfaces.

## Stale Dependency Alerts

Symptom:

- GitHub shows old dependency alerts after source policy changed.
- A Dependabot PR targets an ignored or intentionally coordinated runtime baseline.
- Local `dependency-surface` passes, but alert state has not refreshed yet.

Wrong fix:

- Treat a stale alert as proof that local policy failed.
- Merge a runtime baseline PR without the coordinated release process.
- Close alerts by weakening Docker digest pinning or Dependabot policy.

Safe fix:

```bash
python -B scripts/dev.py dependency-surface
python -B scripts/dev.py container-release
python -B scripts/dev.py github-maintenance
```

Use `docs/development_issue_solutions.md` for guarded Dependabot runtime-baseline PR handling. Keep alert state separate from local policy evidence.

## Secret-Scanning Setting Confusion

Symptom:

- `scripts/configure_github_launch.py` dry-runs secret scanning and push-protection setup.
- GitHub UI still shows secret scanning or push protection as disabled, unavailable, or plan-dependent.
- Local safety checks pass.

Wrong fix:

- Claim secret scanning is enabled because the dry-run command exists.
- Commit screenshots of private security settings, account menus, or alert pages.
- Add real or fake secrets to test scanning.

Safe fix:

```bash
python -B scripts/dev.py github-maintenance
python -B scripts/dev.py safety
```

Treat secret scanning and push protection as account-level settings until authenticated maintenance output or GitHub UI evidence confirms them.

## False Positive Secret Alerts

Symptom:

- GitHub reports a possible secret that is actually a fixture, placeholder, or documentation example.
- Local `safety` passes.
- The alert contains account-level UI or private repository metadata.

Wrong fix:

- Paste alert screenshots or secret-like strings into source docs.
- Silence safety checks because one GitHub alert is false positive.
- Publish private alert metadata as evidence.

Safe fix:

```bash
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

Record the technical resolution in neutral terms. Keep alert IDs, screenshots, account names, and private UI outside git unless a reviewed release process explicitly requires redacted evidence.

## Local Safety Scan Confusion

Symptom:

- `python -B scripts/dev.py safety` passes.
- A reviewer asks whether that proves secret scanning and push protection are enabled on GitHub.
- `github-readiness` has warning/manual rows for account-level setup.

Wrong fix:

- Treat local safety as proof of GitHub account settings.
- Remove manual follow-up rows from post-publish docs.
- Claim push protection from local grep or safety output.

Safe fix:

```bash
python -B scripts/dev.py safety
python -B scripts/dev.py github-readiness
python -B scripts/dev.py github-maintenance
```

Local safety proves the tracked source does not contain known public-safety hazards. GitHub security features require account-level verification.

## Review Checklist

- `.github/dependabot.yml` still covers GitHub Actions and all three Dockerfile directories.
- Python Docker semver-minor and semver-major runtime baseline updates remain ignored until a coordinated runtime upgrade is planned.
- `docs/supply_chain_security.md` remains the source for local dependency posture.
- `docs/github_repository_settings.md` remains the source for account-level security setup expectations.
- Secret scanning, push protection, Dependabot alerts, and Dependabot security updates remain manual/account-level claims until verified.
- Private alert screenshots, real secrets, account security pages, and generated alert IDs are not committed.
- `python -B scripts/dev.py dependency-surface`, `python -B scripts/dev.py safety`, and `python -B scripts/dev.py quality` pass after changing dependency or secret-scanning wording.
