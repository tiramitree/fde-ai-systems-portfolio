# Final Demo Runbook

## 1. Start Local Demos

Recommended local command:

```bash
python -B scripts/dev.py start
```

Open:

```text
http://127.0.0.1:8765
http://127.0.0.1:8770
```

Health check:

```bash
python -B scripts/dev.py health
```

Verify the documented API surface and runtime response contracts:

```bash
python -B scripts/dev.py api-docs
python -B scripts/dev.py contracts
```

Run all evals:

```bash
python -B scripts/dev.py evals
```

Prove the GitHub clone path from a temporary directory:

```bash
python -B scripts/dev.py fresh-clone
```

Replay the end-to-end demo path with fresh reset services:

```bash
python -B scripts/dev.py replay
```

Generate release-attachable replay evidence under `out/`:

```bash
python -B scripts/dev.py replay-artifact
```

Export local traces in an OpenTelemetry-compatible JSON shape:

```bash
python -B scripts/dev.py otel-traces
```

Verify response trace IDs, linked audit events, approval records, and blocked-action evidence:

```bash
python -B scripts/dev.py observability
```

Verify the portfolio threat model maps each risk to deterministic controls and evidence:

```bash
python -B scripts/dev.py threat-model
```

Verify public PR review heuristics, the maintainer policy, the runbook, and the PR template still preserve malicious-contribution checks:

```bash
python -B scripts/dev.py pr-policy
```

## 2. Optional Docker Run

Docker was not available in the current local environment, so this config is prepared but not runtime-verified here.

```bash
docker compose up --build
```

## 3. Optional OpenAI Responses API Mode

Default mode is deterministic local behavior for reliable demos.

To test OpenAI routing/generation:

```powershell
$env:OPENAI_API_KEY="..."
$env:OPENAI_MODEL="gpt-5.2"
$env:COPILOT_MODEL_PROVIDER="openai"
$env:OPS_AGENT_MODEL_ROUTER="openai"
```

Then restart the demo servers.

Application-layer controls stay deterministic:

- Project 1 filters permissions and removes unsafe retrieved content before model generation.
- Project 2 enforces approval gates outside the model.

## 4. Demo Sequence

Project 1:

1. Select Alice.
2. Ask: `How many days per week can employees work remotely?`
3. Show citation.
4. Ask: `What is the finance retention plan?`
5. Show abstention and permission-blocked count.
6. Select Morgan.
7. Ask the same finance question.
8. Show allowed finance citation.
9. Run evals.

Project 2:

1. Select Ivy and `case-1001`.
2. Run investigation.
3. Show violation, draft notice, follow-up, and pending approval.
4. Show direct `send_notice` blocked.
5. Approve as supervisor.
6. Show audit event.
7. Run evals.

## 5. Closing Narrative

These two projects demonstrate the core FDE pattern:

- translate a business workflow into a deployable AI system
- implement the application, not just prompts
- add permissions, approval, audit, traces, and evals
- keep unsafe capabilities controlled by application logic
- explain production upgrade paths clearly


