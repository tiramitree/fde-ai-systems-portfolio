# GitHub Repository Settings Screenshot Checklist

Use this page when collecting or reviewing screenshots for GitHub repository setup. Read it with `docs/github_repository_settings.md`, `docs/post_publish_checklist.md`, `docs/post_publish_warning_examples.md`, `docs/github_repository_metadata_troubleshooting_examples.md`, `docs/stale_repository_topics_evidence_examples.md`, `docs/dependabot_secret_scanning_verification_examples.md`, `docs/stale_dependabot_alert_evidence_examples.md`, `docs/branch_protection_verification_examples.md`, `docs/stale_branch_protection_screenshot_examples.md`, `docs/github_release_page_troubleshooting_examples.md`, `docs/github_release_attachment_screenshot_checklist.md`, `docs/profile_pin_verification_examples.md`, `docs/stale_profile_pin_evidence_examples.md`, `docs/social_preview_verification_examples.md`, `docs/stale_social_preview_cache_examples.md`, and `docs/command_output_troubleshooting_map.md`.

The core rule: local docs, authenticated settings screenshots, and public repository evidence prove different things. Do not commit private account screenshots or claim settings are current until public/account-level evidence confirms them.

## Expected Evidence Split

Local source-of-truth evidence:

```bash
python -B scripts/dev.py launch-assets
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

Remote/public repository evidence:

```bash
python -B scripts/post_publish_check.py
python -B scripts/dev.py github-readiness
```

Authenticated/account-level planning evidence:

```bash
python -B scripts/dev.py github-maintenance
```

Screenshots are supporting review artifacts. They can help a maintainer compare account settings with the tracked checklist, but they are not a replacement for the public repository state, readiness output, or reviewed maintenance command path.

## Description And Topics Screenshots

Capture only when repository metadata is being applied or reviewed.

Useful screenshot evidence:

- repository title, description, and topics visible in repository settings or the public repository header
- the repository owner/name visible enough to avoid confusing a fork or similarly named repo
- no browser profile names, private bookmarks, account emails, tokens, or local file paths

Wrong use:

- claiming metadata is current from `docs/github_repository_settings.md` alone
- committing a full account settings screenshot with private sidebars or account details
- changing the tracked topic list to match an accidental partial setup

Review with:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/dev.py github-maintenance
```

Use `docs/github_repository_metadata_troubleshooting_examples.md` when description, topics, or repository URL state is missing or stale. Use `docs/stale_repository_topics_evidence_examples.md` before treating old topic screenshots, wrong topic slugs, unauthenticated API warning rows, cached repository cards, or private account UI crops as current repository-topic evidence.

## Security Settings Screenshots

Capture only when Dependabot, secret scanning, push protection, or security-alert evidence is being reviewed.

Useful screenshot evidence:

- repository identity clear enough to distinguish this repository from forks or older repositories
- alert scope, dependency path, or Security tab row visible enough to compare with `.github/dependabot.yml`
- no alert tokens, account menus, profile details, private repository lists, browser profile names, local paths, or unrelated private organization settings

Wrong use:

- claiming Dependabot or secret-scanning setup from local source policy alone
- treating an old Security tab screenshot as current alert evidence
- committing private Security tab crops, alert IDs, account menus, or token-adjacent UI

Review with:

```bash
python -B scripts/dev.py dependency-surface
python -B scripts/dev.py safety
python -B scripts/dev.py github-readiness
```

Use `docs/dependabot_secret_scanning_verification_examples.md` before claiming Dependabot or secret-scanning setup is current. Use `docs/stale_dependabot_alert_evidence_examples.md` before treating old security alert screenshots, wrong dependency scopes, dismissed alert rows, private security-tab crops, or local safety-scan output as current repository security-setting evidence.

## Branch Protection Screenshots

Capture only when branch protection is being enabled, reviewed, or debugged.

Useful screenshot evidence:

- `main` branch rule target
- required pull request review setting
- required `quality-gate` status check
- force-push protection state
- enough repository identity to prove the screenshot belongs to this repository

Wrong use:

- treating the checked-in JSON payload as remote branch protection proof
- treating a screenshot of a draft rule as applied policy
- exposing private organization settings or unrelated repository rules

Review with:

```bash
python -B scripts/dev.py governance
python -B scripts/dev.py github-readiness
```

Use `docs/branch_protection_verification_examples.md` before claiming the remote branch policy is active. Use `docs/stale_branch_protection_screenshot_examples.md` before treating old branch-rule screenshots, wrong branch names, API warning rows, inherited organization policy screenshots, or private account UI crops as current branch-protection evidence.

## Social Preview Screenshots

Capture only when the uploaded repository social preview is being checked.

Useful screenshot evidence:

- repository social preview setting showing the image that matches `docs/assets/github-preview.png`
- public repository card or share preview when it visibly matches the intended image
- timestamp or review note kept outside source control if cache delay is being investigated

Wrong use:

- claiming social preview setup from local PNG existence
- committing private account settings screenshots
- treating third-party cached previews as GitHub setting proof

Review with:

```bash
python -B scripts/dev.py assets
python -B scripts/dev.py github-readiness
```

Use `docs/social_preview_verification_examples.md` when the preview is missing, stale, wrong, cached, or confused with profile-pin evidence. Use `docs/stale_social_preview_cache_examples.md` before treating old social-preview images, wrong uploaded images, cache delays, profile-pin confusion, or private account UI crops as current social-preview evidence.

## Release Page Screenshots

Capture only when the release page, latest release, or release attachments are being reviewed.

Useful screenshot evidence:

- release tag `v0.1.0`
- release title and notes matching `docs/github_release_notes_v0.1.0.md`
- current replay artifact attachment names or reviewed links
- latest-release state when the page exists but selection is ambiguous

Wrong use:

- claiming release readiness from local replay artifacts alone
- committing generated `out/` files as a substitute for release-page evidence
- using an old release page screenshot after the release notes or artifacts changed

Review with:

```bash
python -B scripts/dev.py replay-artifact
python -B scripts/dev.py github-readiness
```

Use `docs/github_release_page_troubleshooting_examples.md`, `docs/github_latest_release_troubleshooting_examples.md`, `docs/release_attachment_verification_examples.md`, and `docs/github_release_attachment_screenshot_checklist.md` before claiming the release page is current.

## Profile Pin Screenshots

Capture only when checking whether `tiramitree/fde-ai-systems-portfolio` is pinned on the public GitHub profile.

Useful screenshot evidence:

- public profile page showing the intended repository pinned
- repository card identity clear enough to distinguish it from forks or older repos
- browser chrome cropped or redacted so account/session details are not exposed

Wrong use:

- claiming profile pin setup from repository reachability, stars, topics, or social preview
- committing private account profile settings screenshots
- asking contributors for account screenshots, secrets, or collaborator access

Review with:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/post_publish_check.py
```

Use `docs/profile_pin_verification_examples.md` before claiming profile-pin setup. Use `docs/stale_profile_pin_evidence_examples.md` before treating old profile screenshots, wrong pinned repositories, stale profile caches, social-preview confusion, or private account UI crops as current profile-pin evidence.

## Screenshot Handling Rules

- Keep screenshots outside git unless a release process explicitly requests a reviewed, redacted artifact.
- Crop or redact browser chrome, account menus, notifications, email addresses, private repository lists, local paths, and tokens.
- Prefer public repository pages over authenticated settings pages when public evidence can prove the same claim.
- Pair every screenshot claim with the command or doc that owns the relevant evidence boundary.
- Delete temporary screenshots after review if they contain account-level UI, even when no secret is visible.

## Review Checklist

- `docs/github_repository_settings.md` remains the source of truth for expected repository settings.
- `python -B scripts/dev.py github-readiness` has no hard failures when the GitHub API is reachable.
- Description/topics screenshots are compared with `docs/github_repository_metadata_troubleshooting_examples.md`.
- Stale repository-topic evidence is compared with `docs/stale_repository_topics_evidence_examples.md`.
- Security settings screenshots are compared with `docs/dependabot_secret_scanning_verification_examples.md`.
- Stale Dependabot alert evidence is compared with `docs/stale_dependabot_alert_evidence_examples.md`.
- Branch protection screenshots are compared with `docs/branch_protection_verification_examples.md`.
- Stale branch-protection screenshots are compared with `docs/stale_branch_protection_screenshot_examples.md`.
- Social preview screenshots are compared with `docs/social_preview_verification_examples.md`.
- Stale social-preview cache evidence is compared with `docs/stale_social_preview_cache_examples.md`.
- Release page screenshots are compared with `docs/github_release_page_troubleshooting_examples.md`, `docs/github_latest_release_troubleshooting_examples.md`, `docs/release_attachment_verification_examples.md`, and `docs/github_release_attachment_screenshot_checklist.md`.
- Profile pin screenshots are compared with `docs/profile_pin_verification_examples.md`.
- Stale profile-pin evidence is compared with `docs/stale_profile_pin_evidence_examples.md`.
- Public docs do not claim metadata, branch protection, social preview, release page, or profile pin setup from local docs alone.
- Private account screenshots, personal account details, and local paths are not committed.
