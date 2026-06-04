# Star Growth Plan

Goal: make the repository useful and differentiated enough that engineers save and recommend it as a practical reference. Stars should be a byproduct of usefulness, not the primary product goal.

## Audience

- engineers building enterprise AI pilots
- forward-deployed engineering practitioners
- AI application engineers
- solution engineers
- technical reviewers

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
- learning project reference

## Content Pieces

1. README with diagrams and screenshots.
2. 3 to 5 minute demo video.
3. Technical blog post: "The model is not the security boundary."
4. Short post: "Three enterprise AI reference systems that run without paid APIs."
5. Red-team eval pack follow-up.

Ready-to-use copy lives in `docs/launch_copy_pack.md`.
The recording checklist lives in `docs/demo_recording_checklist.md`.
Run `python -B scripts/dev.py launch-assets` before posting so required channels, issue materials, and anti-hype language stay aligned.

## First Issue Labels

Create issues for:

- add FastAPI adapter
- add PostgreSQL storage adapter prototype
- add per-case eval regression reports
- add red-team eval pack
- add a compact README Docker verification evidence pointer
- run and publish Docker verification from `python -B scripts/dev.py docker-runtime`

These give contributors clear entry points and connect public issues to real engineering work.

## Anti-Hype Rule

Do not claim production readiness. Claim practical reference value.

Good:

> Runnable reference implementations for enterprise AI control patterns.

Avoid:

> Fully finished enterprise AI platform.

Prefer:

> Enterprise AI control-pattern reference implementation.
