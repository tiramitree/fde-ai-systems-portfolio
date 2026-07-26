# Release Completion Audit

Date: 2026-06-02

This audit records the current release-facing evidence for the repository. It is intentionally conservative: unverified external integrations are listed as remaining blockers instead of being claimed as complete.

## Runtime

Evidence commands:

```bash
python -B scripts/dev.py health
python -B scripts/dev.py smoke
python -B scripts/dev.py replay
```

Expected local services:

- Secure Enterprise Knowledge Copilot: `http://127.0.0.1:8765`
- Regulated Customer Operations Agent: `http://127.0.0.1:8770`
- AI Reliability Incident Console: `http://127.0.0.1:8780`

Status: local Python runtime is the verified primary path.

Remaining external blocker:

- Docker runtime must be verified on a Docker-enabled machine with `python -B scripts/dev.py docker-runtime`.

## System Scope

Evidence:

- `README.md`
- `PROJECT_CONTENT_INDEX.md`
- `docs/project_case_notes.md`
- `docs/technical_review_playbook.md`
- per-project architecture, threat model, demo script, and technical review notes

Status: the repository documents three enterprise AI control systems: secure RAG, governed workflow automation, and release reliability triage.

## Eval Gates

Evidence command:

```bash
python -B scripts/dev.py evals
```

Expected result:

- Project 1: 14/14 passed, unsafe leak failures 0
- Project 2: 8/8 passed, unsafe direct side-effect failures 0
- Project 3: 6/6 passed, unsafe release approval failures 0

Status: eval gates cover permission safety, approval safety, and release reliability decisions.

## Public Repository Hygiene

Evidence commands:

```bash
python -B scripts/dev.py safety
python -B scripts/dev.py launch-assets
python -B scripts/dev.py governance
python -B scripts/dev.py workflow-security
python -B scripts/dev.py pr-policy
```

Status: public content, contribution policy, workflow security, and review policy are gated by scripts.

## Model Runtime

Default mode is deterministic and local-first. Optional OpenAI Responses API integration exists for Project 1 and Project 2; the reliability console remains a deterministic release-decision gate:

- `secure-enterprise-knowledge-copilot/src/copilot/model_gateway.py`
- `regulated-customer-operations-agent/src/ops_agent/model_gateway.py`

Remaining external blocker:

- Live OpenAI mode requires a valid API key and should be verified with `python -B scripts/dev.py openai-live` before being claimed as runtime evidence.

## Current Release Decision

The repository is suitable for local technical review after the full local gate passes:

```bash
python -B scripts/dev.py verify
```

Do not claim these items as complete until separately verified:

1. Docker runtime proof.
2. Live OpenAI mode proof.
3. GitHub branch protection and release page setup.
4. Social preview configured in GitHub UI.
5. Real launch feedback or star-growth evidence.
