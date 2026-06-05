# Stale Profile-Pin Evidence Examples

Use this page when GitHub profile-pin screenshots, profile cache state, wrong pinned repositories, social-preview cards, or private account UI crops may no longer prove the current profile pin. Read it with `docs/profile_pin_verification_examples.md`, `docs/social_preview_verification_examples.md`, `docs/github_repository_settings_screenshot_checklist.md`, and `docs/post_publish_warning_examples.md`.

The core rule: repository metadata, social preview, profile pin setup, account UI screenshots, and source docs prove different things. Do not claim a profile pin is current until visible profile evidence confirms it.

## Expected Evidence Split

Local launch proof:

```bash
python -B scripts/dev.py launch-assets
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

Public/account-level follow-up:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/post_publish_check.py
```

Profile screenshots are review aids. They can help compare the visible GitHub profile with the intended repository, but they do not replace the public profile page, account-level setup, or readiness warning rows.

Review old profile screenshots, wrong pinned repositories, stale profile caches, social-preview confusion, and private account UI crops as separate evidence surfaces.

## Old Profile Screenshots

Use this when a screenshot shows the profile pin from an earlier source or account state.

Symptom:

- The screenshot shows a pinned repository, but the capture predates a repository rename, launch update, or profile change.
- The screenshot is reused in launch copy as if it proves the current public profile.
- The visible profile card cannot be tied to the current repository URL.

Wrong fix:

- Claim the profile pin is current from the old screenshot.
- Edit repository docs to match an old profile card.
- Commit a stale profile screenshot as source evidence.

Safe fix:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/dev.py launch-assets
```

Use `docs/profile_pin_verification_examples.md` to verify the current public profile. Keep profile-pin claims manual until the visible profile page shows the intended repository.

## Wrong Pinned Repositories

Use this when the profile has pins, but not the intended repository.

Symptom:

- A similarly named repository is pinned.
- An older fork or prototype appears in the pinned area.
- Public launch docs point to `tiramitree/fde-ai-systems-portfolio`, but the profile card points elsewhere.

Wrong fix:

- Claim profile setup is done because any repository is pinned.
- Change README links to match the accidental profile pin.
- Ask contributors for account access or profile screenshots.

Safe fix:

```bash
git remote -v
python -B scripts/dev.py github-readiness
```

Update the account-level pin, not the source docs, unless the repository identity intentionally changes. Keep repository metadata, profile pin setup, and launch copy separate.

## Stale Profile Caches

Use this when the intended pin was changed, but a browser, signed-in view, signed-out view, or cached page still shows older profile state.

Symptom:

- The maintainer sees one profile state while a public or fresh browser view shows another.
- `github-readiness` has no hard failures, but manual profile evidence remains unclear.
- A launch reviewer sees an older profile card after account-level changes.

Wrong fix:

- Treat a cached browser view as the source of truth.
- Claim profile setup from a maintainer-only settings view.
- Remove the manual follow-up before visible public evidence exists.

Safe fix:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/dev.py launch-assets
```

Check the public profile in a fresh or signed-out view. Describe cache delay as account-level follow-up, not as source-code failure.

## Social-Preview Confusion

Use this when a polished repository social preview is mistaken for a profile pin.

Symptom:

- `docs/assets/github-preview.png` exists and social preview setup is reviewed.
- The repository card looks current, but the profile still does not pin the repository.
- Launch copy treats social preview setup as account-profile setup.

Wrong fix:

- Treat social preview upload as profile-pin evidence.
- Mark all GitHub manual rows done after one account setting is updated.
- Use the social preview image as proof that the repository appears on the profile.

Safe fix:

```bash
python -B scripts/dev.py assets
python -B scripts/dev.py github-readiness
```

Use `docs/social_preview_verification_examples.md` for the social preview and `docs/profile_pin_verification_examples.md` for the profile pin. The card image and the pinned profile slot are different account-level surfaces.

## Private Account UI Crops

Use this when profile-pin evidence includes signed-in GitHub UI, account menus, notifications, private repository lists, browser profile details, or local machine details.

Symptom:

- The screenshot includes account chrome or authenticated profile controls.
- A private repository list, notification count, profile avatar menu, or browser identity is visible.
- The image is being considered for source docs or public launch material.

Wrong fix:

- Commit authenticated profile screenshots as public evidence.
- Crop only the obvious account menu while leaving private UI clues.
- Ask contributors to provide their own account screenshots.

Safe fix:

```bash
python -B scripts/dev.py safety
python -B scripts/dev.py launch-assets
```

Prefer public profile URLs, readiness output, or a neutral maintainer note kept outside git. Source docs should record the technical finding, not private account UI.

## Review Checklist

- `docs/profile_pin_verification_examples.md` remains the source for profile-pin evidence boundaries.
- `docs/social_preview_verification_examples.md` remains the source for social-preview evidence boundaries.
- `docs/github_repository_settings_screenshot_checklist.md` remains the source for screenshot handling.
- `docs/post_publish_warning_examples.md` remains the source when local docs and remote public evidence disagree.
- Repository metadata, social preview, profile pin setup, account UI screenshots, and source docs stay separate.
- Old profile screenshots, wrong pinned repositories, stale profile caches, social-preview confusion, and private account UI crops are reviewed against visible profile evidence.
- Private account screenshots, account menus, notifications, private repository lists, local paths, browser profile details, and tokens are not committed.
- Do not claim a profile pin is current until visible profile evidence confirms it.
- `python -B scripts/dev.py github-readiness` remains the public/account-level follow-up command.
- `python -B scripts/dev.py launch-assets`, `python -B scripts/dev.py safety`, and `python -B scripts/dev.py quality` pass after changing profile-pin wording.
