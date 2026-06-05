# GitHub Profile Pin Verification Examples

Use this page when checking whether the repository is pinned on the GitHub profile. Read it with `docs/github_repository_settings.md`, `docs/github_repository_settings_screenshot_checklist.md`, `docs/stale_profile_pin_evidence_examples.md`, `docs/social_preview_verification_examples.md`, `docs/stale_social_preview_cache_examples.md`, `docs/post_publish_checklist.md`, `docs/post_publish_warning_examples.md`, and `docs/command_output_troubleshooting_map.md`.

The core rule: repository readiness, social preview setup, and profile pin setup prove different things. Do not claim the profile pin is configured until account-profile evidence confirms it.

## Expected Evidence Split

Repository readiness evidence:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/dev.py github-maintenance
```

Local launch evidence:

```bash
python -B scripts/dev.py launch-assets
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

Account-profile evidence is a visible GitHub profile page or authenticated account settings view that shows `tiramitree/fde-ai-systems-portfolio` pinned. Local commands can keep the manual row visible, but they do not prove the public profile pin by themselves.

## Missing Profile Pin

Symptom:

- `github-readiness` prints `[MANUAL] profile repository pin configured`.
- The repository page is reachable.
- The GitHub profile does not show `fde-ai-systems-portfolio` in the pinned repositories area.

Wrong fix:

- Claim the profile pin from repository reachability.
- Remove the manual readiness row.
- Treat stars, forks, topics, or social preview setup as profile-pin evidence.

Safe fix:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/dev.py github-maintenance
```

Pin the repository from GitHub account profile settings. Keep the manual row visible until the public profile shows the intended repository.

## Wrong Pinned Repository

Symptom:

- The profile has pinned repositories, but not `tiramitree/fde-ai-systems-portfolio`.
- A similarly named or older repository is pinned.
- README and launch docs point to the intended repository.

Wrong fix:

- Change public docs to match the accidentally pinned repository.
- Claim profile setup is done because any repository is pinned.
- Ask contributors for account access to fix the profile.

Safe fix:

```bash
git remote -v
python -B scripts/dev.py github-readiness
```

Use `docs/github_repository_settings.md` as the source of truth for the intended repository. Update the account-level pin, not the project docs, unless the repository identity intentionally changes.

## Stale Profile Cache

Symptom:

- The profile pin was changed in GitHub settings.
- The public profile or browser still shows an older pinned state.
- Local readiness has no hard failures, but manual profile evidence is not yet visible.

Wrong fix:

- Claim the profile pin is current from a maintainer-only settings view.
- Rewrite launch copy around a cached profile state.
- Treat a browser cache as source-of-truth evidence.

Safe fix:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/dev.py launch-assets
```

Check the public profile in a fresh browser session or signed-out view. Keep public wording conservative until the visible profile page shows the intended pin.

## Social-Preview Confusion

Symptom:

- `docs/assets/github-preview.png` exists and social preview setup is reviewed.
- The profile still does not pin the repository.
- `github-readiness` reports manual rows for both social preview and profile repository pin.

Wrong fix:

- Treat social preview upload as profile pin evidence.
- Mark all account-level GitHub setup done after one repository settings action.
- Remove the profile pin from manual follow-up because the repository card looks polished.

Safe fix:

```bash
python -B scripts/dev.py launch-assets
python -B scripts/dev.py github-readiness
```

Use `docs/social_preview_verification_examples.md` for social preview state, then verify the profile pin separately from the account profile. The repository card image and the profile pin are different account-level settings.

## Account Visibility

Symptom:

- The repository is public, but the profile pin is not visible to a signed-out visitor.
- A maintainer can see the profile setting, but public visitors cannot.
- Post-publish docs still list profile pin setup as manual.

Wrong fix:

- Claim public profile readiness from a private account view.
- Ask contributors to authenticate or share account screenshots.
- Treat repository visibility as account-profile visibility.

Safe fix:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/post_publish_check.py
```

Use public or redacted account-profile evidence. Do not add private account screenshots, local browser profile paths, tokens, or personal account details to the repository.

Use `docs/stale_profile_pin_evidence_examples.md` before treating old profile screenshots, wrong pinned repositories, stale profile caches, social-preview confusion, or private account UI crops as current profile-pin evidence.

Use `docs/stale_social_preview_cache_examples.md` before treating old social-preview images, wrong uploaded images, cache delays, profile-pin confusion, or private account UI crops as profile-pin evidence.

## Review Checklist

- `docs/github_repository_settings.md` still names the intended repository and profile-pin timing.
- `docs/github_repository_settings_screenshot_checklist.md` is used before retaining or sharing profile screenshots.
- `docs/stale_profile_pin_evidence_examples.md` is used before stale profile-pin evidence becomes a public claim.
- `docs/social_preview_verification_examples.md` is used only for social preview evidence.
- `docs/stale_social_preview_cache_examples.md` is used before stale preview-card evidence becomes profile-pin evidence.
- `python -B scripts/dev.py github-readiness` has no hard failures when the GitHub API is reachable.
- `python -B scripts/dev.py launch-assets` passes after release-facing wording changes.
- `python -B scripts/dev.py safety` passes before committing public docs.
- `python -B scripts/dev.py quality` passes before merging release-facing wording changes.
- Repository readiness, social preview setup, and profile pin setup are reviewed separately.
- Public docs do not claim the profile pin is configured until account-profile evidence confirms it.
