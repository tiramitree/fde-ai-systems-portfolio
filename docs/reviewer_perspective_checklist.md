# Reviewer Perspective Checklist

Use this before showing the repo to an interviewer, recruiter, or GitHub audience.

## First 30 Seconds

- The README says what the repo is without hype.
- The visual preview shows two distinct systems.
- The first paragraph explains why this is different from chatbot demos.
- The quickstart is visible without scrolling too far.
- The project does not claim to be production-ready.

## User Clone Experience

- `python -B scripts/dev.py verify` works from a clean checkout.
- The local demo does not require OpenAI API keys.
- The command entrypoint is cross-platform.
- Runtime artifacts are ignored.
- The user can open two local URLs and see meaningful UI.
- Error messages are not raw stack traces in the browser.
- Trace IDs, audit events, approval records, and blocked actions can be verified with `python -B scripts/dev.py observability`.

## Interviewer Skepticism

Expected challenges:

- "This is local JSON, not production."
- "The prompt-injection detection is simple."
- "The model is optional."
- "Docker was not verified here."

Approved answer:

> Correct. The repo is a local-first portfolio that demonstrates the control boundaries. The production path is documented. The important thing is that permissions, approval gates, audit, traces, and evals are explicit and testable instead of hidden inside prompts.

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
