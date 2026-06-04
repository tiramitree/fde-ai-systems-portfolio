# README Navigation Drift Examples

Use this page when README.md, PROJECT_CONTENT_INDEX.md, or a linked docs page stops matching the current repository. Read it with `docs/readme_navigation_audit.md`, `docs/command_output_troubleshooting_map.md`, and `docs/docs_only_review_comment_examples.md`.

Navigation drift is a release risk because readers use README.md as the public map of the project. A small stale link or unsupported claim can make a working local system look unreliable, overstate evidence, or send contributors to the wrong gate.

## Review Rules

- Keep fixes narrow and tied to the smallest changed file.
- Update README.md and PROJECT_CONTENT_INDEX.md together when a new public doc is added.
- Do not claim Docker runtime, OpenAI live mode, GitHub release, branch protection, social preview, profile pin, or launch feedback from README text alone.
- Do not add secrets, private paths, external accounts, paid-service requirements, generated runtime files, real customer data, or environment dumps.
- Do not hide a failing gate by deleting the link, weakening the claim, or moving evidence into ignored generated artifacts.

## Stale Link

Symptom:

```text
README.md links to docs/example_old_name.md, but the file was renamed or removed.
```

Risk:

- readers hit a broken public link
- `python -B scripts/dev.py assets` fails
- a useful doc can look missing even when a replacement exists

Safer fix:

```text
Update README.md to the current file path, update PROJECT_CONTENT_INDEX.md if the doc is public-facing, and keep the surrounding description unchanged unless the source doc changed too.
```

Verify:

```bash
git diff -- README.md PROJECT_CONTENT_INDEX.md docs/
python -B scripts/dev.py assets
python -B scripts/dev.py safety
```

Reviewer comment:

```text
Please keep this as a link repair only. The replacement path is fine, but the surrounding claim should not broaden unless the linked source doc and evidence command changed too.
```

## Unsupported Claim

Symptom:

```text
README.md says Docker runtime verification is complete, but only static container hygiene has been checked.
```

Risk:

- static config evidence is mistaken for runtime proof
- environment-dependent claims look current before the required machine or account-level action exists
- launch copy becomes stronger than the evidence matrix

Safer fix:

```text
Change the README wording to point to the checklist or command without claiming completion. Use docs/readme_navigation_audit.md to find the supporting doc and owner gate.
```

Good:

```text
Docker runtime evidence checklist: see docs/docker_runtime_evidence_checklist.md. Run `python -B scripts/dev.py docker-runtime` only on a Docker-enabled machine.
```

Avoid:

```text
Docker runtime verification is complete.
```

Verify:

```bash
python -B scripts/dev.py claims
python -B scripts/dev.py launch-assets
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

Reviewer comment:

```text
This needs narrower wording. The README can point to the runtime checklist, but it should not claim current Docker runtime proof until the matching command has passed in a Docker-enabled environment.
```

## Missing Source Doc

Symptom:

```text
README.md adds a new readiness pointer, but no supporting docs page explains the workflow, owner gate, or safe failure path.
```

Risk:

- README becomes a table of promises instead of navigable evidence
- contributors cannot find the first local command to run
- reviewers cannot tell whether the claim is release-facing, optional, account-level, or local-only

Safer fix:

```text
Add or update the smallest supporting docs page first, then link it from README.md and PROJECT_CONTENT_INDEX.md. Include the local verification command and any manual-evidence limits.
```

Verify:

```bash
python -B scripts/dev.py community-issues
python -B scripts/dev.py assets
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

Reviewer comment:

```text
The README pointer is useful, but it needs a source doc before merge. Please add the smallest supporting docs page with the owner gate, safe failure mode, and local verification command, then link it from PROJECT_CONTENT_INDEX.md.
```

## Manual Evidence Drift

Symptom:

```text
README.md or docs/published_repository_status.md describes a GitHub release page, branch protection, social preview, profile pin, Docker runtime result, or OpenAI live-mode result as current after the evidence has gone stale.
```

Risk:

- account-level or environment-dependent proof is treated like checked-in source evidence
- public readers cannot reproduce the claim from the repo alone
- maintainers may approve release copy before remote state is verified

Safer fix:

```text
Move the wording back to a checklist or pending/manual status until the matching command or account-level proof is refreshed. Keep local source docs honest about what is verified from the checkout.
```

Verify:

```bash
python -B scripts/dev.py assets
python -B scripts/dev.py launch-assets
python -B scripts/dev.py github-readiness
python -B scripts/dev.py fresh-clone-local
```

Reviewer comment:

```text
Please separate local source evidence from manual or account-level evidence here. The README can point to the check, but the current completion claim should wait until the matching remote or environment-specific proof is refreshed.
```

## Drift Review Checklist

Before approving a README navigation fix:

```bash
git diff --stat
git diff -- README.md PROJECT_CONTENT_INDEX.md docs/
git diff --check
python -B scripts/dev.py assets
python -B scripts/dev.py community-issues
python -B scripts/dev.py launch-assets
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

Run `python -B scripts/dev.py fresh-clone-local` when the change affects setup paths, public docs navigation, runtime paths, screenshots, release-facing claims, or manual evidence wording.

Use `docs/docs_only_review_comment_examples.md` for the final approve, request-changes, close-as-unsafe, or close-as-low-signal response. Use `docs/command_output_troubleshooting_map.md` for the first local fix when a gate fails.
