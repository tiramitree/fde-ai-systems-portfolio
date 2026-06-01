# GitHub Launch Plan

## Repository Positioning

Suggested repo name:

```text
fde-ai-systems-portfolio
```

Suggested tagline:

```text
Two runnable enterprise AI systems showing secure RAG, governed agents, evals, traces, audit logs, and approval gates.
```

## Why People Might Star It

- It is not another chatbot template.
- It shows two complete enterprise AI workflows.
- It runs locally without paid APIs.
- It includes evals and smoke tests.
- It demonstrates security and governance patterns interviewers ask about.
- It includes production upgrade notes.

## Launch Checklist

- [x] Confirm README renders well on GitHub.
- [x] Add visual README assets.
- [x] Replace static quality badge with GitHub Actions badge after publishing.
- [x] Add screenshots.
- [x] Add short README GIF.
- [x] Run all evals and smoke tests.
- [ ] Add repo topics:
  - `ai-agents`
  - `rag`
  - `llm-evals`
  - `forward-deployed-engineering`
  - `enterprise-ai`
  - `openai`
  - `agentic-workflows`
- [ ] Apply repository settings from `docs/github_repository_settings.md`.
- [x] Run `python -B scripts/post_publish_check.py`.
- [x] Convert `docs/community_backlog.md` into initial public issues.
- [x] Create the first public issues from `docs/github_initial_issues.md`.
- [x] Record the first lightweight demo GIF using `docs/demo_recording_checklist.md`.
- [x] Add a deterministic launch asset hygiene gate through `python -B scripts/dev.py launch-assets`.
- [ ] Publish launch copy from `docs/launch_copy_pack.md`.
- [ ] Publish a short technical post.
- [ ] Pin the repo on GitHub profile.

## README Hook

Lead with the problem:

> Most AI app demos stop at chat. Real enterprise deployments need permissions, citations, approval gates, audit logs, traces, and evals. This repo implements those patterns in two runnable systems.

## Launch Post Draft

I built a small open-source portfolio of enterprise AI systems:

- Secure Enterprise Knowledge Copilot: permission-aware RAG with citations, abstention, prompt-injection handling, traces, audit logs, and evals.
- Regulated Customer Operations Agent: governed tool-calling workflow with approval queues, side-effect blocking, supervisor approval, audit logs, traces, and unsafe-action evals.

It runs locally without paid APIs, but includes optional OpenAI Responses API integration points and a production upgrade path.

The goal is to show what AI apps need after the chatbot stage: governance, observability, and quality gates.
