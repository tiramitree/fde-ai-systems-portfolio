# Public Release Audit

Purpose: prevent the GitHub version from exposing weak, misleading, broken, or embarrassing details.

## Release Positioning

Do say:

- This is a local-first enterprise AI systems reference repository.
- It demonstrates secure RAG and governed agent workflows.
- It runs without paid APIs.
- Optional OpenAI Responses API integration points exist.
- Production adapters are documented as upgrade paths.

Do not say:

- This is production-ready.
- This is a complete replacement for enterprise auth, workflow, or compliance systems.
- It already uses a real vector database.
- It already has verified Docker runtime if Docker has not been tested.
- It has live GPT-5.2 behavior unless an API-key run has been verified.

## Known Weak Points And How To Frame Them

## 1. Local JSON Store

Potential criticism:

> Why are you using JSON files instead of a database?

Answer:

> The local demo uses JSON for zero-dependency reproducibility. The control design is the point: permission filtering, approval gates, traces, audit, and evals. The production upgrade path is PostgreSQL with row-level security, pgvector, migrations, and transactional audit writes.

## 2. Deterministic Local Logic

Potential criticism:

> This does not fully use an LLM.

Answer:

> Correct. The default path is deterministic so demos and evals are stable without an API key. Optional OpenAI gateway code exists. More importantly, the security controls are intentionally outside the model, which should be preserved in production.

## 3. Prompt Injection Detection Is Simple

Potential criticism:

> Regex injection detection is not enough.

Answer:

> Correct. The current implementation demonstrates the boundary: retrieved content is data, not instructions, and suspicious evidence is excluded. Production should add provenance scoring, classifiers, model-based review, allowlists, and red-team evals.

## 4. Docker Not Locally Verified

Potential criticism:

> Docker config exists but was not tested.

Answer:

> The config is included for standard deployment shape. The current verified path is Python local runtime because Docker is unavailable in this environment. The repo now has `python -B scripts/dev.py docker-runtime` as the tracked Docker-enabled runtime proof.

## 5. No Real Auth Provider

Potential criticism:

> Users are mocked.

Answer:

> Yes. The repository focuses on system boundaries. Production would integrate an IdP and enforce tenant/role claims at the API and database level.

## Public Repo Must Not Include

- API keys
- real personal/company data, including legal names, phone numbers, personal email addresses, local usernames, chat export paths, or private private community files
- private private community files
- temp SQLite files
- runtime JSON state
- logs
- pycache files
- claims that unverified integrations are verified

## Before Publishing

Run:

```bash
python -B scripts/dev.py safety
python -B scripts/dev.py verify
```

Manual checks:

- README is clear in the first viewport.
- Demo commands work from a clean clone.
- Known limitations are honest.
- No private files are included.
- No generated runtime state is tracked.
- The repo has LICENSE, CONTRIBUTING, SECURITY, ROADMAP, issue templates, and PR template.
