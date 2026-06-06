Initial public release with three local-first enterprise AI systems:

- Secure Enterprise Knowledge Copilot for permission-aware RAG.
- Regulated Customer Operations Agent for governed tool-calling workflows.
- AI Reliability Incident Console for release eval regression and rollout triage.

Verified locally:

- Project 1 evals: 11/11 passed, unsafe leaks 0.
- Project 2 evals: 8/8 passed, unsafe direct side-effect failures 0.
- Project 3 evals: 6/6 passed, unsafe release approval failures 0.
- Smoke tests: 13/13 passed.
- API contract checks: 68/68 passed.
- Quality gate: passed.

This release is designed for engineering review: it shows permission boundaries, citations, abstention, approval gates, release gates, traces, audit logs, evals, replay scripts, and production upgrade paths.
