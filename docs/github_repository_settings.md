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
docs/assets/github-preview.svg
```

If GitHub requires a bitmap upload, export the SVG to PNG before uploading.

## Branch Protection

Recommended for `main` after the first push:

- require pull request before merging
- require status checks before merging
- require `quality-gate` to pass
- require branches to be up to date before merging
- disallow force pushes

## First Release

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

- Project 1 evals: 7/7 passed, unsafe leaks 0.
- Project 2 evals: 5/5 passed, unsafe direct side-effect failures 0.
- Smoke tests: 9/9 passed.
- Quality gate: passed.
```

## Profile Pin

Pin this repository only after:

- GitHub Actions is green.
- README screenshots render correctly.
- repo topics are set.
- static badge is replaced with the real Actions badge.

