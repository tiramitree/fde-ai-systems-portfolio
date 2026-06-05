# Social Preview Verification Examples

Use this page when checking the repository social preview after a push. Read it with `docs/github_repository_settings.md`, `docs/github_repository_settings_screenshot_checklist.md`, `docs/profile_pin_verification_examples.md`, `docs/stale_profile_pin_evidence_examples.md`, `docs/post_publish_checklist.md`, `docs/post_publish_warning_examples.md`, and `docs/command_output_troubleshooting_map.md`.

The core rule: local image asset existence and GitHub account-level social preview setup prove different things. Do not claim social preview setup until the GitHub UI or account-level evidence confirms it.

## Expected Evidence Split

Local asset proof:

```bash
python -B scripts/dev.py assets
python -B scripts/dev.py launch-assets
```

These commands prove that `docs/assets/github-preview.png` exists, matches the expected asset checks, and is referenced by the launch docs.

Account-level proof:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/dev.py github-maintenance
```

These commands surface GitHub readiness state and the guarded maintenance path, but the social preview upload is still a manual/account-level check unless authenticated evidence confirms it.

## Missing Social Preview

Symptom:

- `github-readiness` prints `[MANUAL] social preview configured`.
- The repository page still shows GitHub's default preview.
- `docs/assets/github-preview.png` exists locally.

Wrong fix:

- Claim social preview setup because the PNG exists.
- Remove the manual readiness row.
- Replace the preview asset without checking whether the GitHub UI has the image uploaded.

Safe fix:

```bash
python -B scripts/dev.py assets
python -B scripts/dev.py github-readiness
```

Open repository settings and upload `docs/assets/github-preview.png` as the social preview. Keep the checklist row manual until the GitHub page shows the expected image.

## Stale Preview Image

Symptom:

- The repository page has a social preview, but it does not match `docs/assets/github-preview.png`.
- A recent asset refresh changed local files.
- Local visual asset checks pass.

Wrong fix:

- Treat the old uploaded image as current because local checks pass.
- Claim the public repository uses the latest preview before re-uploading it.

Safe fix:

```bash
python -B scripts/dev.py assets
python -B scripts/dev.py launch-assets
```

Compare the visible GitHub preview with `docs/assets/github-preview.png`. Re-upload the PNG if the account-level setting is stale, then rerun readiness.

## Wrong Uploaded Image

Symptom:

- The GitHub preview exists, but it uses a screenshot, logo crop, or outdated image instead of the intended preview.
- `docs/github_repository_settings.md` points to `docs/assets/github-preview.png`.

Wrong fix:

- Update docs to match the accidental upload.
- Leave the wrong image because the repository has some preview image.

Safe fix:

```bash
python -B scripts/dev.py assets
python -B scripts/dev.py safety
```

Use `docs/github_repository_settings.md` as the source of truth. Upload the intended PNG and keep public docs conservative until the visible GitHub card matches it.

## Cache Delay

Symptom:

- The correct social preview was uploaded.
- The repository page or a shared link still shows an older cached image.
- `github-readiness` has no hard failures, but manual rows remain.

Wrong fix:

- Rewrite local docs to match a cached third-party preview.
- Claim every external preview cache has refreshed.

Safe fix:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/dev.py launch-assets
```

Record the GitHub UI state separately from third-party cache behavior. Only claim the GitHub repository setting after the GitHub page itself shows the expected preview.

## Profile-Pin Confusion

Symptom:

- The repository social preview is checked, but the GitHub profile still does not pin the repository.
- `github-readiness` reports manual rows for both social preview and profile repository pin.

Wrong fix:

- Treat social preview upload as profile pin evidence.
- Claim account setup is finished after only one manual action.

Safe fix:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/dev.py github-maintenance
```

Handle the social preview and profile pin as separate account-level actions. Use `docs/profile_pin_verification_examples.md` for profile-pin evidence, and use `docs/post_publish_checklist.md` to keep both manual rows visible until each one has direct evidence.

Use `docs/stale_profile_pin_evidence_examples.md` before treating a polished repository card, old profile screenshot, or stale profile cache as profile-pin evidence.

## Review Checklist

- `docs/assets/github-preview.png` exists and passes `python -B scripts/dev.py assets`.
- `docs/github_repository_settings.md` still names `docs/assets/github-preview.png` as the intended upload.
- `docs/github_repository_settings_screenshot_checklist.md` is used before retaining or sharing social preview screenshots.
- `docs/stale_profile_pin_evidence_examples.md` is used before social-preview evidence is reused as profile-pin evidence.
- `python -B scripts/dev.py launch-assets` passes after any launch-doc wording change.
- `python -B scripts/dev.py quality` passes before merging release-facing wording changes.
- `python -B scripts/dev.py github-readiness` has no hard failures.
- Manual rows stay manual until GitHub UI or authenticated account-level evidence confirms the setting.
- Social preview setup and profile pin setup are reviewed as separate actions.
- Public docs do not claim social preview setup from local image checks alone.
