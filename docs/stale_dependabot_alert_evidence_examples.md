# Stale Dependabot Alert Evidence Examples

Use this page when old security alert screenshots, wrong dependency scopes, dismissed alert rows, private security-tab crops, or local safety-scan output may no longer prove the current repository security-setting state. Read it with `docs/dependabot_secret_scanning_verification_examples.md`, `docs/github_repository_settings_screenshot_checklist.md`, `docs/post_publish_warning_examples.md`, and `docs/post_publish_checklist.md`.

The core rule: checked-in Dependabot config, account-level security settings, current security-alert rows, private security-tab screenshots, local safety-scan output, and source docs prove different things. Do not claim Dependabot or secret-scanning alert evidence is current until GitHub readiness or authenticated evidence confirms it.

The stale evidence set includes old security alert screenshots, wrong dependency scopes, dismissed alert rows, private security-tab crops, and local safety-scan output.

## Expected Evidence Split

Local dependency policy evidence:

```bash
python -B scripts/dev.py dependency-surface
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

Remote/account-level evidence:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/dev.py github-maintenance
```

Publication evidence after push:

```bash
python -B scripts/post_publish_check.py
```

Use `docs/dependabot_secret_scanning_verification_examples.md` to verify the current dependency-monitoring and secret-scanning evidence boundary. Keep Dependabot and secret-scanning alert claims manual until current readiness or authenticated evidence confirms them.

## Old Security Alert Screenshots

Symptom:

- A copied Security tab screenshot shows old Dependabot or secret-scanning alerts.
- The screenshot was taken before dependency policy, Docker pins, or repository settings changed.
- Local `dependency-surface` and `safety` output no longer match the screenshot state.

Wrong fix:

- Treat the old screenshot as current alert evidence.
- Rewrite source policy to match a stale alert screenshot.
- Claim repository security settings are current from the screenshot alone.

Safe fix:

```bash
python -B scripts/dev.py dependency-surface
python -B scripts/dev.py safety
python -B scripts/dev.py github-readiness
```

Keep old screenshots as historical context only. A security-alert screenshot is current evidence only when it matches current source policy and current repository evidence.

## Wrong Dependency Scopes

Symptom:

- A Dependabot alert references a package manager, directory, or manifest outside the tracked policy.
- A screenshot or alert row confuses Docker base-image monitoring with Python package monitoring.
- A contributor assumes the alert proves a missing runtime dependency.

Wrong fix:

- Add broad package manifests just to make the alert disappear.
- Weaken the stdlib-first posture to satisfy an unrelated alert scope.
- Remove Docker digest pinning or Dependabot ignores without a coordinated runtime upgrade.

Safe fix:

```bash
python -B scripts/dev.py dependency-surface
python -B scripts/dev.py container-release
```

Use `.github/dependabot.yml` and `docs/supply_chain_security.md` as the source policy. Treat wrong-scope alerts as triage evidence, not as a reason to expand dependencies casually.

## Dismissed Alert Rows

Symptom:

- GitHub shows a dismissed, resolved, or stale alert row.
- Local policy changed after the alert was dismissed.
- A reviewer asks whether the dismissal proves the repository is clean.

Wrong fix:

- Claim all security alerts are current from a dismissed row.
- Hide local safety or dependency-surface failures behind an old dismissal.
- Paste alert identifiers, private comments, or account metadata into docs.

Safe fix:

```bash
python -B scripts/dev.py safety
python -B scripts/dev.py dependency-surface
python -B scripts/dev.py github-readiness
```

Dismissal rows are account-level history. They do not replace current source scans, current repository settings, or readiness output.

## Private Security-Tab Crops

Symptom:

- A screenshot shows private Security tab rows, alert identifiers, organization policy, or account menus.
- The crop includes private repository names, profile details, notifications, browser profile data, or token-adjacent UI.
- The screenshot does not prove what a public reviewer can see.

Wrong fix:

- Commit private Security tab screenshots as proof.
- Ask contributors for private account-level screenshots.
- Publish alert IDs, account names, browser profile details, or local paths.

Safe fix:

```bash
python -B scripts/dev.py safety
python -B scripts/dev.py launch-assets
python -B scripts/dev.py github-readiness
```

Private security screenshots, account menus, notifications, private repository lists, local paths, browser profile details, alert IDs, and tokens are not committed. Use public evidence and conservative status wording instead.

## Local Safety-Scan Output

Symptom:

- `python -B scripts/dev.py safety` passes.
- GitHub still shows manual or warning rows for Dependabot alerts, Dependabot security updates, secret scanning, or push protection.
- A public status update wants to claim the GitHub Security tab is clean.

Wrong fix:

- Treat local safety output as proof of GitHub account-level settings.
- Remove manual setup rows because local grep passed.
- Claim current Dependabot or secret-scanning alert state before authenticated evidence exists.

Safe fix:

```bash
python -B scripts/dev.py safety
python -B scripts/dev.py dependency-surface
python -B scripts/dev.py github-maintenance
python -B scripts/dev.py github-readiness
```

Local safety output proves the tracked source has no known public-safety hazards. It does not prove GitHub security features, alerts, or account-level policy are current.

## Review Checklist

- `docs/dependabot_secret_scanning_verification_examples.md` remains the source for current dependency-monitoring and secret-scanning evidence boundaries.
- Old security alert screenshots, wrong dependency scopes, dismissed alert rows, private security-tab crops, and local safety-scan output are not treated as current repository security-setting evidence.
- Checked-in Dependabot config, account-level security settings, current security-alert rows, private security-tab screenshots, local safety-scan output, and source docs stay separate.
- Security-tab screenshots are review aids; they do not replace GitHub readiness output, authenticated maintenance evidence, current alert rows, or source-policy checks.
- Private security screenshots, account menus, notifications, private repository lists, local paths, browser profile details, alert IDs, and tokens are not committed.
- `python -B scripts/dev.py dependency-surface` passes before changing dependency-monitoring wording.
- `python -B scripts/dev.py safety` passes before publishing docs.
- `python -B scripts/dev.py github-readiness` remains the public/account-level follow-up command.
- `python -B scripts/dev.py github-maintenance` remains the authenticated account-level planning command.
- `python -B scripts/dev.py launch-assets` passes before public launch copy references alert evidence.
- `python -B scripts/dev.py quality` passes before push-facing work.
- `python -B scripts/post_publish_check.py` is used only after the intended push is visible.
