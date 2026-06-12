# Demo Recording Checklist

Use this checklist to record the first GIF or 3-5 minute video.

## Before Recording

```powershell
cd <repo-root>
python -B scripts/dev.py verify
python -B scripts/dev.py start
```

Open:

- `http://127.0.0.1:8765`
- `http://127.0.0.1:8770`
- `http://127.0.0.1:8780`

Browser setup:

- 1280x720 or 1440x900 viewport.
- Hide bookmarks bar if it distracts.
- Use light theme unless the OS forces another theme.
- Close unrelated tabs.
- Keep terminal font readable.

## Recording Flow

### 1. Opening

Show README first.

Say:

```text
This is a local-first repository of enterprise AI control patterns: secure RAG, governed agents, release reliability, evals, traces, audit logs, and approval gates.
```

### 2. Project 1

Open Project 1.

Run:

```text
How many days per week can employees work remotely?
```

Show:

- answer
- citation
- trace/audit panel if visible

Run as Alice:

```text
What is the finance retention plan?
```

Show:

- abstention
- blocked evidence count

Switch to Morgan and run:

```text
What is the finance retention plan?
```

Show:

- authorized answer
- finance citation

### 3. Project 2

Open Project 2.

Run:

```text
Check whether Market Blue still has an active listing for the recalled RX-900 product.
```

Show:

- tool calls
- violation creation
- notice draft
- follow-up
- approval request
- blocked direct side-effect

Approve as supervisor.

Show:

- notice sent once
- audit record

### 4. Project 3

Open Project 3.

Run triage for:

```text
inc-2026-014
```

Show:

- linked failed evals
- blocked rollout decision
- remediation steps
- trace/audit evidence

Switch to:

```text
inc-2026-015
```

Show:

- latency-only monitor decision
- no unsafe rollout block

### 5. Quality Gate

Show terminal:

```powershell
python -B scripts/dev.py verify
```

Show final lines:

- Project 1 eval 14/14
- Project 2 eval 8/8
- Project 3 eval 6/6
- smoke tests 13/13
- quality gate passed

## After Recording

Save assets under:

```text
docs/assets/
```

Suggested filenames:

```text
docs/assets/fde-ai-systems-demo.gif
docs/assets/fde-ai-systems-demo.mp4
```

Then update:

- `README.md`
- `docs/demo_video_script.md`
- `docs/completion_checklist.md`
- `docs/final_completion_audit.md`

Finally run:

```powershell
python -B scripts/dev.py verify
git status --short
```
