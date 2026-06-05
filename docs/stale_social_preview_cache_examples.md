# Stale Social-Preview Cache Examples

Use this page when old social-preview images, wrong uploaded images, cache delays, profile-pin confusion, or private account UI crops may no longer prove the current GitHub social preview. Read it with `docs/social_preview_verification_examples.md`, `docs/profile_pin_verification_examples.md`, `docs/stale_profile_pin_evidence_examples.md`, `docs/github_repository_settings_screenshot_checklist.md`, and `docs/post_publish_warning_examples.md`.

The core rule: local preview assets, uploaded social preview, cached cards, profile pin setup, account UI screenshots, and source docs prove different things. Do not claim social preview setup is current until visible GitHub evidence confirms it.

## Expected Evidence Split

Local asset proof:

```bash
python -B scripts/dev.py assets
python -B scripts/dev.py launch-assets
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

Public/account-level follow-up:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/post_publish_check.py
```

Social-preview screenshots are review aids. They can help compare a visible GitHub card with `docs/assets/github-preview.png`, but they do not replace the GitHub repository settings page, the public repository card, or readiness warning rows.

Review old social-preview images, wrong uploaded images, cache delays, profile-pin confusion, and private account UI crops as separate evidence surfaces.

## Old Social-Preview Images

Use this when a shared card, screenshot, or browser cache shows a preview image from an earlier launch state.

Symptom:

- The visible card has the old title, old screenshot, or old product framing.
- `docs/assets/github-preview.png` has changed and passes local asset checks.
- Launch copy reuses a screenshot as if it proves the current GitHub card.

Wrong fix:

- Claim the current social preview from an old card screenshot.
- Edit source docs to match stale cached imagery.
- Commit an old social-preview screenshot as current evidence.

Safe fix:

```bash
python -B scripts/dev.py assets
python -B scripts/dev.py github-readiness
```

Use `docs/social_preview_verification_examples.md` to verify the current GitHub social preview. Keep social-preview claims manual until the visible GitHub repository card matches the intended asset.

## Wrong Uploaded Images

Use this when the repository has a social preview, but the uploaded image is not the intended `docs/assets/github-preview.png`.

Symptom:

- The card shows a logo crop, old screenshot, default image, or unrelated upload.
- The repository settings note points to `docs/assets/github-preview.png`.
- Local asset checks pass, but public visual evidence disagrees.

Wrong fix:

- Treat any uploaded image as the intended social preview.
- Change README or launch copy to match the accidental image.
- Mark all account-level setup complete after finding a preview card.

Safe fix:

```bash
python -B scripts/dev.py assets
python -B scripts/dev.py launch-assets
```

Upload the intended asset in GitHub repository settings. Keep uploaded image evidence separate from local asset existence and from cached third-party cards.

## Cache Delays

Use this when the correct social preview was uploaded, but GitHub, browser, or third-party link previews still show older imagery.

Symptom:

- GitHub settings show one preview while shared links or cached cards show another.
- A fresh browser view and signed-in view disagree.
- `github-readiness` has no hard failures, but the visible preview evidence is still mixed.

Wrong fix:

- Treat a stale shared-card cache as the GitHub source of truth.
- Claim every external link preview has refreshed.
- Remove manual follow-up before visible public evidence is consistent.

Safe fix:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/dev.py launch-assets
```

Separate GitHub repository evidence from browser or third-party cache evidence. Describe cache delay as account-level follow-up, not as a source-code failure.

## Profile-Pin Confusion

Use this when a polished repository social preview is mistaken for the repository being pinned on the GitHub profile.

Symptom:

- The repository card image is current, but the GitHub profile does not pin the repository.
- A profile screenshot shows a repository card, but not the intended pinned slot.
- Launch docs treat social preview setup as profile-pin setup.

Wrong fix:

- Treat social preview upload as profile-pin evidence.
- Claim all manual GitHub account rows are done after one visible card updates.
- Use the social preview card as proof that the repository is pinned.

Safe fix:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/dev.py launch-assets
```

Use `docs/profile_pin_verification_examples.md` and `docs/stale_profile_pin_evidence_examples.md` for profile-pin evidence. The repository card image and the pinned profile slot are different account-level surfaces.

## Private Account UI Crops

Use this when social-preview evidence includes signed-in GitHub settings, account menus, notifications, private repository lists, browser profile details, or local machine details.

Symptom:

- The screenshot includes authenticated GitHub settings around the social preview upload.
- A browser profile, local path, account menu, notification count, or private repository list is visible.
- The image is being considered for source docs or public launch material.

Wrong fix:

- Commit authenticated settings screenshots as public evidence.
- Crop only the obvious account menu while leaving private UI clues.
- Ask contributors to provide social-preview screenshots from their own accounts.

Safe fix:

```bash
python -B scripts/dev.py safety
python -B scripts/dev.py launch-assets
```

Prefer public repository cards, readiness output, or a neutral maintainer note kept outside git. Source docs should record the technical finding, not private account UI.

## Review Checklist

- `docs/social_preview_verification_examples.md` remains the source for social-preview evidence boundaries.
- `docs/profile_pin_verification_examples.md` remains the source for profile-pin evidence boundaries.
- `docs/stale_profile_pin_evidence_examples.md` remains the source before preview cards become profile-pin evidence.
- `docs/github_repository_settings_screenshot_checklist.md` remains the source for screenshot handling.
- `docs/post_publish_warning_examples.md` remains the source when local docs and remote public evidence disagree.
- Local preview assets, uploaded social preview, cached cards, profile pin setup, account UI screenshots, and source docs stay separate.
- Old social-preview images, wrong uploaded images, cache delays, profile-pin confusion, and private account UI crops are reviewed against visible GitHub evidence.
- Private account screenshots, account menus, notifications, private repository lists, local paths, browser profile details, and tokens are not committed.
- Do not claim social preview setup is current until visible GitHub evidence confirms it.
- `python -B scripts/dev.py github-readiness` remains the public/account-level follow-up command.
- `python -B scripts/dev.py assets`, `python -B scripts/dev.py launch-assets`, `python -B scripts/dev.py safety`, and `python -B scripts/dev.py quality` pass after changing social-preview wording.
