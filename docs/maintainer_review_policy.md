# Maintainer Review Policy

Purpose: keep public contributions useful without letting low-signal, unsafe, or phishing-like activity shape the project.

## Accept Or Adapt

Useful reviews and pull requests are worth addressing when they are:

- specific about a bug, security gap, eval weakness, broken workflow, or unclear documentation
- consistent with the local-first, dependency-light demo path
- explicit about changed files and expected behavior
- willing to pass `python -B scripts/dev.py verify`
- compatible with the core rule that permissions, approvals, audit, traces, and evals live in application code

For these, the maintainer may:

- request changes
- rewrite the idea directly in a safer form
- add a follow-up issue
- merge only after review, CI, and public-safety checks pass

## Ignore Or Close

Reviews, issues, or pull requests should be ignored, closed, or treated as spam when they:

- ask for secrets, tokens, private files, account details, local paths, or personal data
- include unrelated links, downloads, binaries, obfuscated code, or instructions to run unknown commands
- weaken permission checks, approval gates, audit logging, traces, evals, or local reproducibility
- add required paid APIs, network calls, or dependencies to the default demo path without a strong reason
- change the pinned Python container runtime baseline without a coordinated release-policy update across Dockerfiles, docs, and verification evidence
- create noisy refactors without improving a repository claim
- pressure the maintainer to grant collaborator access
- hide eval failures, mask CI failures, or silently write generated artifacts

## Pull Request Gate

Before merging any external PR:

1. Read the diff before running it.
2. Check for secret exfiltration, local file reads, network calls, subprocess calls, dependency installs, generated artifacts, and environment variable access.
3. Run triage before running contributor code:

```bash
python -B scripts/dev.py pr-triage
python -B scripts/dev.py governance
python -B scripts/dev.py workflow-security
```

4. Run:

```bash
python -B scripts/dev.py safety
python -B scripts/dev.py verify
```

5. Confirm no tracked runtime state, logs, caches, local paths, or personal identifiers were added.
6. Confirm GitHub Actions is green. External PR workflows that require approval should be approved only after the diff review is clean.
7. Merge only if the contribution strengthens the public repository or an explicit roadmap item.

See [Pull Request Review Runbook](pr_review_runbook.md) for the concrete review sequence. Use [Public Roadmap Issue Comment Examples](public_roadmap_issue_comment_examples.md) before accepting, narrowing, closing, or linking public roadmap issue work. Use [GitHub Discussions Launch Checklist](github_discussions_launch_checklist.md) before enabling Discussions, pinning starter topics, or treating discussion feedback as launch evidence. Use [GitHub Authenticated Maintenance Troubleshooting Examples](github_authenticated_maintenance_troubleshooting_examples.md) before treating dry-run maintenance output as applied repository state, and use [GitHub Public PR API Fallback Troubleshooting Examples](github_public_pr_api_fallback_troubleshooting_examples.md) before treating public pulls page visibility as file-level triage evidence.

## Current External PR Rule

Issue-aligned contributions are welcome, but the project does not merge PRs merely because they run locally. The bar is:

- useful feature
- narrow scope
- no hidden side effects
- no privacy leaks
- no weakened safety boundary
- passing local and CI gates
