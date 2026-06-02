# Portfolio Threat Model

This repository is a local-first demonstration of enterprise AI control boundaries. It is not production software, but the security model is intentionally explicit so a reviewer can ask, "What can go wrong, and what proves the control still works?"

Core principle:

```text
The model is not the security boundary. Permissions, side effects, audit, traces, and eval success are enforced by application code and verified by gates.
```

## Assets

| Asset | Why It Matters |
| --- | --- |
| Internal documents and citations | Users must not receive evidence they cannot access. |
| User identity and role | Retrieval and approval behavior depends on role. |
| Retrieved evidence and prompt context | Retrieved text may contain untrusted instructions. |
| Case, seller, listing, approval, and notice state | Agent side effects must be controlled and auditable. |
| API keys and local environment values | Secrets must stay outside the public repository and browser-visible errors. |
| Audit events, traces, eval runs, and release docs | Evidence must explain behavior without leaking private material. |
| GitHub Actions and public PR workflow | External contributors must not gain write tokens or secrets through CI. |

## Threat Matrix

| ID | Threat | Deterministic Control | Evidence |
| --- | --- | --- | --- |
| T01 | Unauthorized document disclosure | Project 1 filters by tenant and role before answer generation; inaccessible chunks are counted but not passed as answer evidence. | `python -B scripts/dev.py evals`, `python -B scripts/dev.py smoke`, `python -B scripts/dev.py observability` |
| T02 | User or retrieved-content prompt injection | User messages are rejected before retrieval when they match injection patterns; retrieved unsafe lines are treated as data and removed from evidence. | `python -B scripts/dev.py evals`, `python -B scripts/dev.py smoke`, `python -B scripts/dev.py observability` |
| T03 | Unsupported or fabricated answers | The answer layer abstains when accessible evidence does not clear the threshold or citation requirements. | `python -B scripts/dev.py evals`, `python -B scripts/dev.py claims` |
| T04 | External side effect without approval | Project 2 blocks direct side-effect tools for investigator users and creates approval requests instead. | `python -B scripts/dev.py evals`, `python -B scripts/dev.py smoke`, `python -B scripts/dev.py observability` |
| T05 | Approval bypass or non-supervisor approval | Approval execution is supervisor-only; bypass instructions create refusal evidence instead of approvals. | `python -B scripts/dev.py evals`, `python -B scripts/dev.py contracts`, `python -B scripts/dev.py observability` |
| T06 | Duplicate side-effect execution | Approval requests use idempotency keys and already-processed approvals return without sending duplicate notices. | `python -B scripts/dev.py smoke`, `python -B scripts/dev.py observability` |
| T07 | Secret, private path, or internal exception leakage | Public files are scanned for secret-like and local-machine markers; unexpected backend exceptions return generic JSON errors. | `python -B scripts/dev.py safety`, `python -B scripts/dev.py error-hygiene` |
| T08 | Public PR or CI workflow abuse | GitHub Actions run with read-only permissions, safe triggers, hardened checkout, no secrets, and CODEOWNERS/governance plus PR-review-policy checks. | `python -B scripts/dev.py workflow-security`, `python -B scripts/dev.py governance`, `python -B scripts/dev.py pr-policy`, `python -B scripts/dev.py pr-triage` |
| T09 | Dependency or supply-chain drift | Local runtime stays stdlib-first; Docker bases are digest-pinned; Dependabot covers allowed update surfaces. | `python -B scripts/dev.py dependency-surface` |
| T10 | Optional model gateway weakens controls or leaks keys | OpenAI mode is opt-in, key references are constrained, structured outputs are required, and failures fall back locally. | `python -B scripts/dev.py model-gateway-safety` |
| T11 | Trace, audit, or approval evidence does not explain behavior | Observability integrity checks connect responses to persisted trace IDs, audit events, blocked actions, and approval records. | `python -B scripts/dev.py observability`, `python -B scripts/dev.py otel-traces` |
| T12 | Browser/static route surprises | Runtime UI contracts verify content types, basic safety headers, JSON 404s, and traversal blocking. | `python -B scripts/dev.py ui-contracts` |

## Trust Boundaries

| Boundary | Trusted Component | Untrusted Input | Rule |
| --- | --- | --- | --- |
| Retrieval | `retrieval.py` role/tenant filter | user question and document corpus | Filter before evidence assembly. |
| Answering | `answering.py` and `security.py` | user text and retrieved text | Cite accessible evidence or abstain. |
| Agent tools | `tools.py` and `agent.py` | user request and model/router output | Side effects require deterministic approval. |
| Approval | `approve_action` and approval endpoint | approval ID and requester role | Supervisor-only execution. |
| Model gateway | project `model_gateway.py` files | model output and API availability | Optional model output cannot authorize access or side effects. |
| Public repo | safety, dependency, workflow, governance, and PR-policy gates | contributor code and public docs | No secrets, no privileged CI, no unreviewed security-boundary changes, and no weakened review heuristics. |
| UI runtime | project `app.py` files | path input and browser requests | Serve known local assets with explicit security headers. |

## Production Controls To Add

- Real authentication and session management.
- PostgreSQL row-level security and transactionally persisted traces/audit events.
- Immutable audit/event storage with retention and redaction policies.
- Policy-as-code for retrieval permissions, tool authorization, and approval routing.
- OpenTelemetry SDK instrumentation around API handlers, retrieval, model calls, tool calls, approvals, and audit writes.
- Connector-scoped credentials, rate limits, retry policies, and transactional outbox processing for external side effects.
- Red-team eval ingestion from production incidents and support tickets.

## Technical Review Framing

Use this concise answer:

```text
I separate threats into information disclosure, prompt injection, unsafe side effects, evidence gaps, public-repo supply-chain risk, and optional model-provider risk. The important part is that each control has a deterministic owner and a command that proves it. The model can help draft or classify, but the app decides what evidence is visible, what tools can execute, and what gets recorded for audit.
```
