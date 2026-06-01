# GitHub Repository Settings

Use this checklist immediately after creating the GitHub repository.

## Name

```text
fde-ai-systems-portfolio
```

## Description

```text
Two runnable enterprise AI systems showing secure RAG, governed agents, evals, traces, audit logs, and approval gates.
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
python -B scripts/configure_github_launch.py --apply --skip-release
```

The setup script also tries to enable secret scanning and push protection through `gh repo edit`. That step is best effort because availability can depend on account and repository security settings.

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
- secret scanning and push protection, if they were not already enabled by `python -B scripts/configure_github_launch.py --apply`

## First Release

Automated path after `gh auth login`:

```powershell
python -B scripts/configure_github_launch.py --apply
```

Manual release details if using the GitHub UI:

Create release:

```text
v0.1.0
```

Release title:

```text
FDE AI Systems Portfolio v0.1.0
```

Release notes:

```text
Initial public release with two local-first enterprise AI systems:

- Secure Enterprise Knowledge Copilot for permission-aware RAG.
- Regulated Customer Operations Agent for governed tool-calling workflows.

Verified locally:

- Project 1 evals: 11/11 passed, unsafe leaks 0.
- Project 2 evals: 8/8 passed, unsafe direct side-effect failures 0.
- Smoke tests: 9/9 passed.
- Quality gate: passed.
```

## Profile Pin

Pin this repository only after:

- GitHub Actions is green.
- README screenshots render correctly.
- repo topics are set.
- static badge is replaced with the real Actions badge.
