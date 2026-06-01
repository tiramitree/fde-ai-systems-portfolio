Initial public release with two local-first enterprise AI systems:

- Secure Enterprise Knowledge Copilot for permission-aware RAG.
- Regulated Customer Operations Agent for governed tool-calling workflows.

Verified locally:

- Project 1 evals: 11/11 passed, unsafe leaks 0.
- Project 2 evals: 8/8 passed, unsafe direct side-effect failures 0.
- Smoke tests: 9/9 passed.
- API contract checks: 22/22 passed.
- Quality gate: passed.

The release is designed for FDE and AI application interviews: it shows permission boundaries, citations, abstention, approval gates, traces, audit logs, evals, replay scripts, and production upgrade paths.
