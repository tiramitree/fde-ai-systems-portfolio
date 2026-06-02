# Reviewer Perspective Checklist

Use this before showing the repo to an technical reviewer, technical reviewer, or GitHub audience.

## First 30 Seconds

- The README says what the repo is without hype.
- The visual preview shows two distinct systems.
- The first paragraph explains why this is different from chatbot demos.
- The quickstart is visible without scrolling too far.
- The project does not claim to be production-ready.

## User Clone Experience

- `python -B scripts/dev.py verify` works from a clean checkout.
- `python -B scripts/dev.py fresh-clone` works against the published repository before sharing broadly.
- The local demo does not require OpenAI API keys.
- The command entrypoint is cross-platform.
- Runtime artifacts are ignored.
- The user can open two local URLs and see meaningful UI.
- The backend API surface is documented and verified with `python -B scripts/dev.py api-docs`.
- Error messages are not raw stack traces in the browser.
- Trace IDs, audit events, approval records, and blocked actions can be verified with `python -B scripts/dev.py observability`.
- Trace IDs can be copied from both demo UIs without selecting raw JSON.
- README screenshots are checked against the visual asset manifest with `python -B scripts/dev.py visual-assets`.
- Threats, deterministic controls, evidence files, and proof commands can be verified with `python -B scripts/dev.py threat-model`.
- Public PR review rules and malicious-contribution heuristics can be verified with `python -B scripts/dev.py pr-policy`.
- Release-attachable replay evidence can be generated with `python -B scripts/dev.py replay-artifact`.
- Docker/Compose release hygiene can be verified without a local Docker daemon with `python -B scripts/dev.py container-release`.
- Docker runtime can be verified on a Docker-enabled machine with `python -B scripts/dev.py docker-runtime`.
- OpenAI live mode can be verified in an API-key environment with `python -B scripts/dev.py openai-live`.

## Technical Reviewer Skepticism

Expected challenges:

- "This is local JSON, not production."
- "The prompt-injection detection is simple."
- "The model is optional."
- "Docker runtime was not verified here."
- "OpenAI live mode was not verified here."

Approved answer:

> Correct. The repo is a local-first reference implementation that demonstrates the control boundaries. The production path is documented. The important thing is that permissions, approval gates, audit, traces, and evals are explicit and testable instead of hidden inside prompts.

For Docker specifically, add:

> The container files are statically gated for ports, health checks, commands, env defaults, and ignored build-context state. The repo also has `python -B scripts/dev.py docker-runtime` for Docker-enabled machines; run that before claiming Docker runtime verification.

For OpenAI specifically, add:

> The default path is local and deterministic. The repo has `python -B scripts/dev.py openai-live` for API-key environments; run that before claiming live OpenAI verification.

## Star-Worthiness

The repo should make a reader think:

- I can run this quickly.
- This covers enterprise AI concerns most demos ignore.
- I can borrow these patterns.
- The docs are honest about limitations.
- The evals and smoke tests are useful.

## Do Not Publish If

- quality gate fails
- README has local machine paths
- demo report is stale or failing
- runtime artifacts are staged
- badge still uses sample owner/repo text
- docs overclaim production readiness
- OpenAI live mode is described as verified without an actual run
