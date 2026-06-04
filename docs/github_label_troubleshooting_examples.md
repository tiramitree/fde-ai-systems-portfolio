# GitHub Label Troubleshooting Examples

Use this page when label sync, issue templates, or the community issue pack drift. Read it with `docs/github_labels.json`, `docs/github_initial_issues.md`, `docs/github_repository_settings.md`, `docs/post_publish_checklist.md`, and `docs/command_output_troubleshooting_map.md`.

The core rule: label sync and public roadmap issue creation are separate actions. Sync labels when repository taxonomy should be current, and create public roadmap issues only when the repository is intentionally ready for open issue work.

## Expected Label Flow

Local validation:

```bash
python -B scripts/dev.py community-issues
```

Dry-run the GitHub maintenance plan:

```bash
python -B scripts/dev.py github-community
```

Apply label sync after authenticated review:

```bash
python -B scripts/manage_community_issues.py --apply
```

Create public roadmap issues only after that is the intended policy:

```bash
python -B scripts/manage_community_issues.py --apply --create-issues
```

## Missing Labels

Symptom:

- `community-issues` reports that an issue or template label is not defined in `docs/github_labels.json`.
- `github-community` dry-run lists a label that does not exist on GitHub yet.
- A contributor issue cannot be created with the expected labels.

Wrong fix:

- Remove labels from issues to make the check pass.
- Create one-off GitHub UI labels that are not tracked in the manifest.
- Create public roadmap issues before label sync is reviewed.

Safe fix:

```bash
python -B scripts/dev.py community-issues
python -B scripts/dev.py github-community
```

If the manifest is correct and the repository is authenticated, sync only labels first:

```bash
python -B scripts/manage_community_issues.py --apply
```

## Color Drift

Symptom:

- A GitHub label exists but its color no longer matches `docs/github_labels.json`.
- The dry-run output shows the manifest color that should be applied.
- Public issue labels look inconsistent across docs, release, security, eval, and frontend work.

Wrong fix:

- Edit screenshots or docs to match a drifted GitHub label.
- Treat a color-only change as a reason to recreate roadmap issues.

Safe fix:

```bash
python -B scripts/dev.py community-issues
python -B scripts/manage_community_issues.py --apply
```

Keep the manifest as the source of truth. Color drift is metadata maintenance, not evidence that issue content should change.

## Template Mismatch

Symptom:

- `community-issues` reports that an issue template label is not defined in `docs/github_labels.json`.
- `.github/ISSUE_TEMPLATE/*.yml` references a label that was renamed or removed.
- GitHub-created issues miss the expected category labels.

Wrong fix:

- Delete labels from templates without updating the issue taxonomy.
- Add a new label only in the template and skip the manifest.

Safe fix:

```bash
python -B scripts/dev.py community-issues
python -B scripts/dev.py safety
```

Update the template and `docs/github_labels.json` together. If the label should be public, confirm it appears in the dry-run plan:

```bash
python -B scripts/dev.py github-community
```

## Dry-Run Output

Symptom:

- `github-community` prints label creation commands but no public issue creation commands.
- The output says community issue creation is disabled.
- A reviewer asks whether the issue pack has been published.

Wrong fix:

- Treat dry-run label commands as proof that GitHub has changed.
- Assume issue creation happened because labels were listed.
- Add `--create-issues` only to make the repository look busy.

Safe fix:

```bash
python -B scripts/dev.py github-community
```

Default dry-run output is a plan. It does not mutate GitHub. Label sync needs `--apply`; public issue creation needs both `--apply` and `--create-issues`.

## Issue-Pack Label Mismatch

Symptom:

- `community-issues` reports a current issue label that is missing from the manifest.
- A completed issue still appears in `docs/community_backlog.md` or `docs/star_growth_plan.md`.
- A new issue title duplicates completed work from `docs/github_initial_issues.md`.

Wrong fix:

- Rename labels in only one file.
- Leave completed work in the active backlog.
- Create an issue with broad wording that is not tied to a real improvement.

Safe fix:

```bash
python -B scripts/dev.py community-issues
python -B scripts/dev.py launch-assets
python -B scripts/dev.py safety
```

Update `docs/github_initial_issues.md`, `docs/community_backlog.md`, `docs/star_growth_plan.md`, and `docs/github_labels.json` as one small change when the public issue queue moves forward.

## Review Checklist

- `docs/github_labels.json` is the source of truth for label name, color, and description.
- `.github/ISSUE_TEMPLATE/*.yml` labels exist in the manifest.
- Current issues in `docs/github_initial_issues.md` have defined labels and concrete acceptance criteria.
- `python -B scripts/dev.py community-issues` passes before any GitHub mutation.
- `python -B scripts/dev.py github-community` is reviewed as a dry-run plan.
- `--apply` syncs labels; `--apply --create-issues` creates public roadmap issues.
- Public roadmap issues are created only when open issue work is intentionally ready to be visible.
