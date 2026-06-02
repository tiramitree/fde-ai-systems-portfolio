# Demo Replay Artifact

Run:

```bash
python -B scripts/dev.py replay-artifact
```

This command starts all demos with reset state, replays the release-critical business flows, and writes release-attachable evidence files under `out/`:

- `out/demo_replay_artifact.md`
- `out/demo_replay_artifact.json`

`out/` is ignored by Git so regenerated trace IDs and local ports do not dirty the repository.

## What It Proves

The artifact captures evidence for:

- Project 1 health
- Alice receiving the cited HR answer
- Alice being blocked from confidential finance evidence
- Morgan receiving the authorized finance answer
- prompt-injection abstention with a recorded security event
- Project 2 health
- investigation creating internal work and an approval request
- bypass request blocked without approval creation
- supervisor approval execution
- populated audit and approval surfaces
- Project 3 health
- unsafe canary incident blocking release rollout
- latency-only incident staying monitor-only
- populated trace evidence for triage decisions

## Release Use

Regenerate the artifact from the release commit, then attach the two `out/` files to a GitHub release or paste the Markdown into technical review notes.

## Technical Review Framing

Use this answer:

```text
The replay artifact turns the live demo path into an auditable evidence bundle. It starts clean services, runs the core permission, approval, and release-triage flows, and writes Markdown plus JSON under `out/` so release evidence can be attached without committing dynamic trace IDs.
```
