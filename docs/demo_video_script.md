# Demo Video Script

Target length: 3 to 5 minutes.

## Opening

Most AI demos stop at chat. This repository shows three enterprise AI systems that handle the controls real deployments need: permissions, citations, approval gates, release gates, traces, audit logs, and evals.

## Segment 1: Secure Enterprise Knowledge Copilot

Show `http://127.0.0.1:8765`.

Narration:

> This is a permission-aware knowledge copilot. Alice is an employee. She can ask about remote work policy and gets a cited answer.

Ask:

```text
How many days per week can employees work remotely?
```

Then:

> Now Alice asks about a confidential finance plan. The system detects that relevant evidence exists but is not accessible to Alice, so it abstains instead of leaking or hallucinating.

Ask:

```text
What is the finance retention plan?
```

Then switch to Morgan:

> Morgan is a manager, so the same question returns a finance citation.

## Segment 2: Regulated Customer Operations Agent

Show `http://127.0.0.1:8770`.

Narration:

> This agent handles a regulated product-recall workflow. It can investigate, create internal records, draft a seller notice, and schedule follow-up. It cannot send the notice directly.

Run:

```text
Check whether Market Blue still has an active listing for the recalled RX-900 product.
```

Point out:

- tool calls
- approval request
- blocked direct side effect
- trace ID copy button for connecting the UI result to audit evidence

Approve as supervisor:

> The notice is only sent after supervisor approval.

## Segment 3: Quality Gate

Show terminal:

```powershell
python -B scripts/dev.py verify
```

Narration:

> The repo includes health checks, evals, smoke tests, and a public-release quality gate. This is what keeps the demo from silently regressing.

## Closing

> The important design choice is that the model is not the security boundary. Permissions, approval gates, audit, traces, and evals live in the application layer.
