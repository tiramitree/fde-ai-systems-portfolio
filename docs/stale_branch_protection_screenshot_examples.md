# Stale Branch-Protection Screenshot Examples

Use this page when old branch-rule screenshots, wrong branch names, API warning rows, inherited organization policy screenshots, or private account UI crops may no longer prove the current GitHub branch-protection state. Read it with `docs/branch_protection_verification_examples.md`, `docs/github_repository_settings_screenshot_checklist.md`, `docs/post_publish_warning_examples.md`, and `docs/post_publish_checklist.md`.

The core rule: local branch-protection payloads, authenticated settings, public/API branch-protection evidence, organization policy screenshots, account UI screenshots, and source docs prove different things. Do not claim branch protection is current until GitHub readiness or authenticated evidence confirms it.

## Expected Evidence Split

Local policy proof:

```bash
python -B scripts/dev.py governance
python -B scripts/dev.py pr-policy
python -B scripts/dev.py workflow-security
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

Public/account-level follow-up:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/dev.py github-maintenance
python -B scripts/post_publish_check.py
```

Branch-protection screenshots are review aids. They can help compare visible GitHub branch rules with `docs/github_branch_protection.json`, but they do not replace GitHub readiness output, authenticated maintenance evidence, or current branch-rule state.

Review old branch-rule screenshots, wrong branch names, API warning rows, inherited organization policy screenshots, and private account UI crops as separate evidence surfaces.

## Old Branch-Rule Screenshots

Use this when a screenshot shows a branch rule from an earlier repository setup or before the current policy payload changed.

Symptom:

- The screenshot predates changes to `docs/github_branch_protection.json`, CODEOWNERS, or required status checks.
- The screenshot does not show enough repository identity to distinguish forks or similarly named repositories.
- Launch docs reuse a screenshot as if it proves the current `main` policy.

Wrong fix:

- Claim branch protection is current from an old screenshot.
- Edit the checked-in payload to match stale screenshot evidence.
- Commit stale branch-rule screenshots as source evidence.

Safe fix:

```bash
python -B scripts/dev.py governance
python -B scripts/dev.py github-readiness
```

Use `docs/branch_protection_verification_examples.md` to verify the current remote branch-protection state. Keep branch-protection claims manual until current readiness or authenticated evidence confirms them.

## Wrong Branch Names

Use this when branch protection exists for a branch other than the intended `main` branch.

Symptom:

- The screenshot shows a rule for `master`, a release branch, or a wildcard that does not protect `main` as intended.
- `github-readiness` still reports `main` as not protected.
- The tracked payload is for `main`, but screenshot evidence points elsewhere.

Wrong fix:

- Treat any protected branch as proof that `main` is protected.
- Rename docs or payloads to match an accidental branch rule.
- Remove the readiness warning before `main` is protected.

Safe fix:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/dev.py github-maintenance
```

Apply or update the intended `main` rule. Keep branch identity visible in review notes while avoiding private account details.

## API Warning Rows

Use this when GitHub API limits, unauthenticated checks, or partial API responses make branch-protection evidence incomplete.

Symptom:

- `github-readiness` reports `[WARN] main branch protection enabled: not protected`, an API warning row, or strict-mode failure.
- Local governance checks pass.
- The API output is too weak to prove current public branch-protection state.

Wrong fix:

- Treat missing API evidence as success.
- Weaken readiness checks so unauthenticated environments look complete.
- Add tokens, account details, or private setup notes to public docs.

Safe fix:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/check_github_readiness.py --strict
```

Keep API warning rows as account-level or remote-freshness follow-up. Authenticated evidence can confirm branch protection, but token values and account details stay outside source control.

## Inherited Organization Policy Screenshots

Use this when screenshots show organization-level rules, rulesets, or inherited policy that may not prove the repository-level `main` protection expected by this project.

Symptom:

- The screenshot shows organization rules, rulesets, or inherited controls without the repository rule target.
- Required `quality-gate`, CODEOWNERS review, stale review dismissal, or force-push settings are unclear.
- A reviewer cannot tell whether the policy applies to `tiramitree/fde-ai-systems-portfolio`.

Wrong fix:

- Treat inherited policy screenshots as proof of this repository's current branch protection.
- Remove repository-level readiness checks because an organization policy appears to exist.
- Commit organization settings screenshots with private account or organization details.

Safe fix:

```bash
python -B scripts/dev.py governance
python -B scripts/dev.py github-readiness
```

Keep organization policy evidence separate from repository branch-rule evidence. Public docs should describe the verification boundary, not private organization settings.

## Private Account UI Crops

Use this when branch-protection evidence includes signed-in GitHub settings, organization menus, private repository lists, notifications, browser profile details, or local machine details.

Symptom:

- A screenshot includes authenticated settings around branch rules or rulesets.
- Account menus, organization names, notification counts, private repository lists, browser profile names, or local paths are visible.
- The screenshot is being considered for source docs or public launch material.

Wrong fix:

- Commit authenticated branch-protection screenshots as public evidence.
- Crop only the obvious account menu while leaving private UI clues.
- Ask contributors to provide screenshots from their own private repositories or organizations.

Safe fix:

```bash
python -B scripts/dev.py safety
python -B scripts/dev.py launch-assets
```

Prefer readiness output, authenticated maintenance summaries without secrets, or a neutral maintainer note kept outside git. Source docs should record the technical finding, not private account UI.

## Review Checklist

- `docs/branch_protection_verification_examples.md` remains the source for branch-protection evidence boundaries.
- `docs/github_repository_settings_screenshot_checklist.md` remains the source for screenshot handling.
- `docs/post_publish_warning_examples.md` remains the source when local docs and remote public evidence disagree.
- `docs/post_publish_checklist.md` keeps branch-protection follow-up visible after publication.
- Local branch-protection payloads, authenticated settings, public/API branch-protection evidence, organization policy screenshots, account UI screenshots, and source docs stay separate.
- Old branch-rule screenshots, wrong branch names, API warning rows, inherited organization policy screenshots, and private account UI crops are reviewed against current GitHub branch-protection evidence.
- Private account screenshots, account menus, notifications, private repository lists, local paths, browser profile details, and tokens are not committed.
- Do not claim branch protection is current until GitHub readiness or authenticated evidence confirms it.
- `python -B scripts/dev.py github-readiness` remains the public/account-level follow-up command.
- `python -B scripts/dev.py governance`, `python -B scripts/dev.py launch-assets`, `python -B scripts/dev.py safety`, and `python -B scripts/dev.py quality` pass after changing branch-protection wording.
