# GitHub Repository Settings

Use this checklist immediately after creating the GitHub repository.

## Name

```text
fde-ai-systems-portfolio
```

## Description

```text
Three runnable enterprise AI systems showing secure RAG, governed agents, AI release reliability, evals, traces, audit logs, and approval gates.
```

## Website

Leave blank until a hosted demo or project page exists.

## Topics

```text
ai-agents
rag
llm-evals
enterprise-ai
forward-deployed-engineering
openai
responses-api
agentic-workflows
tool-calling
human-in-the-loop
ai-safety
python
```

## Social Preview

Use:

```text
docs/assets/github-preview.png
```

The SVG source is also kept at `docs/assets/github-preview.svg`.

## Branch Protection

Recommended for `main` after the first push:

- require pull request before merging
- require status checks before merging
- require `quality-gate` to pass
- require branches to be up to date before merging
- disallow force pushes

Automated path after `gh auth login`:

```powershell
python -B scripts/maintain_github_state.py --apply --skip-release
```

The maintenance script delegates launch setup to `scripts/configure_github_launch.py` and also provides the guarded PR-maintenance path. Secret scanning and push protection are best effort because availability can depend on account and repository security settings.

The branch-protection API payload is tracked in:

```text
docs/github_branch_protection.json
```

The payload expects code-owner review coverage from:

```text
.github/CODEOWNERS
```

## Dependency Monitoring

Dependabot version updates are tracked in:

```text
.github/dependabot.yml
```

After publishing, enable the repository security features available in the GitHub UI:

- Dependabot alerts
- Dependabot security updates
- secret scanning and push protection, if they were not already enabled by `python -B scripts/maintain_github_state.py --apply`

## Labels And Community Issues

Repository labels are tracked in:

```text
docs/github_labels.json
```

Troubleshooting examples live in:

```text
docs/github_label_troubleshooting_examples.md
```

Validate labels, issue templates, and the community issue pack with:

```powershell
python -B scripts/dev.py community-issues
```

Dry-run GitHub label sync:

```powershell
python -B scripts/manage_community_issues.py
```

After `gh auth login`, sync labels without creating roadmap issues:

```powershell
python -B scripts/manage_community_issues.py --apply
```

Create community issues only when the repository is intentionally ready to show open roadmap work:

```powershell
python -B scripts/manage_community_issues.py --apply --create-issues
```

## First Release

Automated path after `gh auth login`:

```powershell
python -B scripts/maintain_github_state.py --apply
```

Manual release details if using the GitHub UI:

Create release:

```text
v0.1.0
```

Release title:

```text
FDE AI Systems Reference v0.1.0
```

Release notes:

```text
Initial public release with three local-first enterprise AI systems:

- Secure Enterprise Knowledge Copilot for permission-aware RAG.
- Regulated Customer Operations Agent for governed tool-calling workflows.
- AI Reliability Incident Console for release eval regression and rollout triage.

Verified locally:

- Project 1 evals: 11/11 passed, unsafe leaks 0.
- Project 2 evals: 8/8 passed, unsafe direct side-effect failures 0.
- Project 3 evals: 6/6 passed, unsafe release approval failures 0.
- Smoke tests: 13/13 passed.
- Quality gate: passed.
```

## Profile Pin

Pin this repository only after:

- GitHub Actions is green.
- README desktop and mobile screenshots render correctly.
- repo topics are set.
- static badge is replaced with the real Actions badge.
