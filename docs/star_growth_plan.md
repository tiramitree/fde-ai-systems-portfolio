# Star Growth Plan

Goal: make the repository useful and differentiated enough that engineers star it as a reference, not just as a personal portfolio.

## Audience

- engineers building enterprise AI pilots
- FDE candidates
- AI application engineer candidates
- solution engineers
- technical interviewers

## Core Message

Most AI app repos show model calls. This repo shows the missing enterprise control layer:

- secure RAG
- governed agents
- evals
- traces
- audit
- approval gates

## Launch Channels

- GitHub profile pin
- LinkedIn technical post
- X / Twitter thread
- Hacker News Show HN
- Reddit communities focused on LLM apps and AI engineering
- school/career project portfolio

## Content Pieces

1. README with diagrams and screenshots.
2. 3 to 5 minute demo video.
3. Technical blog post: "The model is not the security boundary."
4. Short post: "Two enterprise AI demos that run without paid APIs."
5. Red-team eval pack follow-up.

Ready-to-use copy lives in `docs/launch_copy_pack.md`.
The recording checklist lives in `docs/demo_recording_checklist.md`.

## First Issue Labels

Create issues for:

- add FastAPI adapter
- add PostgreSQL adapter
- add OpenAI Agents SDK branch
- add trace grading examples
- run and publish Docker verification from `python -B scripts/dev.py docker-runtime`
- add red-team eval pack

These make the repo look alive and give contributors clear entry points.

## Anti-Hype Rule

Do not claim production readiness. Claim practical reference value.

Good:

> Runnable reference implementations for enterprise AI control patterns.

Avoid:

> Fully finished enterprise AI platform.

Prefer:

> Enterprise AI control-pattern reference implementation.
