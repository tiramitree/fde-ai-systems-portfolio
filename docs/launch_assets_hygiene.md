# Launch Assets Hygiene

This gate keeps the public launch materials complete and honest before the repository is sent to technical reviewers or shared for feedback.

Run it with:

```bash
python -B scripts/dev.py launch-assets
```

## What It Checks

- launch copy exists for GitHub-adjacent short posts, LinkedIn, X / Twitter, Hacker News, Reddit or community posts, and a follow-up blog outline
- the star-growth plan lists the intended audience, launch channels, content pieces, first issue labels, and anti-hype rule
- initial public issues have labels and acceptance criteria
- the community backlog preserves the key safety invariants for secure RAG, governed agents, and eval gates
- README, the project index, the evidence matrix, and post-publish docs link back to the launch materials

## Anti-Hype Boundary

The launch materials can claim that the repo is a runnable reference implementation with secure RAG, governed agents, evals, traces, audit logs, approval gates, optional OpenAI integration points, and Docker release config.

They should not claim these as complete until real evidence exists:

- Docker runtime verification
- OpenAI live-mode verification
- branch protection enabled in GitHub settings, if not yet verified
- GitHub release page published, if not yet verified
- social preview configured
- profile pin configured
- launch feedback or star-growth success
- production readiness

Use "reference implementation", "control pattern", and "local-first repository" language. Avoid presenting the project as a finished enterprise platform.

## When To Run

Run this after changing README positioning, launch posts, GitHub settings docs, issue templates, release docs, or growth plans. The command is also part of `python -B scripts/dev.py quality` so public positioning drift is caught with the normal release gate.
