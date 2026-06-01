# Demo Replay Artifact

Run:

```bash
python -B scripts/dev.py replay-artifact
```

This command starts both demos with reset state, replays the interview-critical business flows, and writes release-attachable evidence files under `out/`:

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

## Release Use

Regenerate the artifact from the release commit, then attach the two `out/` files to a GitHub release or paste the Markdown into interview notes.

## Interview Framing

Use this answer:

```text
The replay artifact turns the live demo path into an auditable evidence bundle. It starts clean services, runs the core permission and approval flows, and writes Markdown plus JSON under `out/` so I can attach the evidence to a release without committing dynamic trace IDs.
```
