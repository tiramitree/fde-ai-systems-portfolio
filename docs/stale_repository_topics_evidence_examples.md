# Stale Repository Topics Evidence Examples

Use this page when old topic screenshots, wrong topic slugs, unauthenticated API warning rows, cached repository cards, or private account UI crops may no longer prove the current GitHub repository topics. Read it with `docs/github_repository_metadata_troubleshooting_examples.md`, `docs/github_repository_settings_screenshot_checklist.md`, `docs/post_publish_warning_examples.md`, and `docs/post_publish_checklist.md`.

The core rule: local docs, authenticated settings, public repository metadata, cached cards, account UI screenshots, and source docs prove different things. Do not claim repository topics are current until GitHub readiness or authenticated evidence confirms them.

## Expected Evidence Split

Local expected settings:

```bash
python -B scripts/dev.py launch-assets
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

Public/account-level follow-up:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/dev.py github-maintenance
python -B scripts/post_publish_check.py
```

Repository-topic screenshots are review aids. They can help compare visible GitHub topics with `docs/github_repository_settings.md`, but they do not replace the GitHub repository settings page, public repository metadata, or readiness warning rows.

Review old topic screenshots, wrong topic slugs, unauthenticated API warning rows, cached repository cards, and private account UI crops as separate evidence surfaces.

## Old Topic Screenshots

Use this when a screenshot shows repository topics from an earlier setup or launch state.

Symptom:

- A screenshot shows topics that predate the current repository positioning.
- The screenshot does not show the current owner/name clearly enough to distinguish forks or similarly named repositories.
- Launch docs reuse the screenshot as if it proves current public topics.

Wrong fix:

- Claim repository topics are current from an old screenshot.
- Edit tracked settings to match the old screenshot.
- Commit stale topic screenshots as source evidence.

Safe fix:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/dev.py launch-assets
```

Use `docs/github_repository_metadata_troubleshooting_examples.md` to verify the current remote metadata state. Keep topic claims manual until visible GitHub metadata or authenticated evidence confirms them.

## Wrong Topic Slugs

Use this when topics exist, but one or more slugs differ from the intended set.

Symptom:

- GitHub displays a similarly named topic, misspelled slug, or partial topic set.
- `docs/github_repository_settings.md` lists the intended topics.
- `github-readiness` reports missing or unexpected topic state.

Wrong fix:

- Treat any related topic as equivalent to the intended slug.
- Remove expected topics from source docs just to clear a warning.
- Claim discoverability work is done while GitHub still shows a partial set.

Safe fix:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/dev.py github-maintenance
```

Apply the intended topic set through GitHub settings or the authenticated maintenance path. Change expected topics only when the repository positioning intentionally changes.

## Unauthenticated API Warning Rows

Use this when GitHub API limits or unauthenticated checks make topic evidence incomplete.

Symptom:

- `github-readiness` reports a warning row for repository topics or API access.
- Local docs and launch assets pass.
- The API output is too weak to prove the current public topic set.

Wrong fix:

- Treat missing API evidence as success.
- Weaken readiness checks so unauthenticated environments look complete.
- Add tokens, account details, or private setup notes to public docs.

Safe fix:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/dev.py github-maintenance
```

Keep API warning rows as account-level or remote-freshness follow-up. Authenticated evidence can confirm topics, but token values and account details stay outside source control.

## Cached Repository Cards

Use this when GitHub cards, external link previews, search snippets, or browser caches show older topic or metadata state.

Symptom:

- The public repository page and a cached card disagree about visible metadata.
- A launch post preview still shows old topics or old repository framing.
- A reviewer sees a stale card after account-level metadata changes.

Wrong fix:

- Treat cached cards as the source of truth.
- Claim every external preview has refreshed.
- Rewrite source docs around stale search or card snippets.

Safe fix:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/post_publish_check.py
```

Separate public repository metadata from cached cards and third-party previews. Describe cache delay as remote-freshness follow-up, not as local source-code evidence.

## Private Account UI Crops

Use this when repository-topic evidence includes signed-in settings, account menus, private repository lists, notifications, browser profile details, or local machine details.

Symptom:

- A screenshot includes the authenticated settings page around topic controls.
- Account menus, notification counts, private repository lists, browser profile names, or local paths are visible.
- The screenshot is being considered for source docs or public launch material.

Wrong fix:

- Commit authenticated settings screenshots as public evidence.
- Crop only the obvious account menu while leaving private UI clues.
- Ask contributors to provide topic screenshots from their own accounts.

Safe fix:

```bash
python -B scripts/dev.py safety
python -B scripts/dev.py launch-assets
```

Prefer public repository metadata, readiness output, or a neutral maintainer note kept outside git. Source docs should record the technical finding, not private account UI.

## Review Checklist

- `docs/github_repository_metadata_troubleshooting_examples.md` remains the source for metadata warning boundaries.
- `docs/github_repository_settings_screenshot_checklist.md` remains the source for screenshot handling.
- `docs/post_publish_warning_examples.md` remains the source when local docs and remote public evidence disagree.
- `docs/post_publish_checklist.md` keeps repository settings and metadata follow-up visible after publication.
- Local docs, authenticated settings, public repository metadata, cached cards, account UI screenshots, and source docs stay separate.
- Old topic screenshots, wrong topic slugs, unauthenticated API warning rows, cached repository cards, and private account UI crops are reviewed against current GitHub metadata evidence.
- Private account screenshots, account menus, notifications, private repository lists, local paths, browser profile details, and tokens are not committed.
- Do not claim repository topics are current until GitHub readiness or authenticated evidence confirms them.
- `python -B scripts/dev.py github-readiness` remains the public/account-level follow-up command.
- `python -B scripts/dev.py launch-assets`, `python -B scripts/dev.py safety`, and `python -B scripts/dev.py quality` pass after changing repository-topic wording.
