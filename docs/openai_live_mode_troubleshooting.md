# OpenAI Live Mode Troubleshooting

Use this page only for the optional live-mode proof:

```bash
python -B scripts/dev.py openai-live
```

The default verified path remains local and deterministic. Do not require paid API access for the normal demo, do not commit API keys, do not print keys in issues or pull requests, and do not ask contributors to share account credentials.

Read this with `docs/model_runtime_configuration.md`, `docs/model_gateway_safety.md`, and `docs/command_output_troubleshooting_map.md`.

## What The Check Proves

`python -B scripts/dev.py openai-live` starts only the two model-facing apps on isolated local ports:

- `secure-enterprise-knowledge-copilot`
- `regulated-customer-operations-agent`

It then verifies:

- Project 1 reports `openai_gateway_enabled=true`
- Project 1 returns `model_provider=openai`
- Project 1 still returns a grounded answer with citations
- Project 2 returns `model_router=openai`
- Project 2 still creates an approval request
- Project 2 still blocks direct side effects

The check does not change the default local mode, does not verify Project 3, and does not prove any account-level GitHub or release evidence.

## Expected Setup

Use a local shell environment. Keep the key out of source files:

```powershell
$env:OPENAI_API_KEY="<set outside git>"
$env:OPENAI_MODEL="gpt-5.2"
$env:OPENAI_REASONING_EFFORT="low"
$env:OPENAI_TEXT_VERBOSITY="low"
$env:COPILOT_MODEL_PROVIDER="openai"
$env:OPS_AGENT_MODEL_ROUTER="openai"
python -B scripts/dev.py openai-live
```

Before running the live proof, the local safety gate should still pass without an API key:

```bash
python -B scripts/dev.py model-gateway-safety
python -B scripts/dev.py safety
```

## Safe Failure Modes

| Symptom | Likely Cause | Safe Next Step |
| --- | --- | --- |
| `OPENAI_API_KEY is not set` | The live check intentionally refuses to run without a key. | Keep using local deterministic mode, or set the key only in the shell session and rerun. |
| Project 1 reports local mode | `COPILOT_MODEL_PROVIDER` is not set to `openai`, the key is missing, or the gateway fell back after an API failure. | Check shell environment variables, then run `python -B scripts/dev.py model-gateway-safety`. |
| Project 2 reports local mode | `OPS_AGENT_MODEL_ROUTER` is not set to `openai`, the key is missing, or the router fell back after an API failure. | Check shell environment variables, then run `python -B scripts/dev.py model-gateway-safety`. |
| Timeout or transient API failure | Network or service availability issue. | Do not weaken fallback behavior; rerun later or continue with local deterministic mode. |
| Malformed response fallback | The gateway rejected an unexpected structured-output shape. | Keep the fallback, inspect model gateway code, and run `python -B scripts/dev.py contracts`. |
| Citation or approval behavior changes | Model-facing behavior may have drifted around the deterministic boundary. | Treat as a blocker for live-mode claims and run `python -B scripts/dev.py quality`. |

## Rollback

To return to the verified local path in the same shell:

```powershell
$env:COPILOT_MODEL_PROVIDER="local"
$env:OPS_AGENT_MODEL_ROUTER="local"
Remove-Item Env:\OPENAI_API_KEY -ErrorAction SilentlyContinue
python -B scripts/dev.py quality
```

Local mode is also the default when those variables are not set.

## Review Guardrails

For issues and PRs:

- never paste API keys, account ids, billing details, private URLs, or local secret paths
- never add a key to `.env.example`, README examples, Dockerfiles, Compose defaults, screenshots, logs, or generated artifacts
- never make OpenAI live mode required for `verify`, `quality`, `smoke`, `evals`, or fresh-clone checks
- never treat model output as the permission, approval, audit, trace, or eval authority
- do not claim live OpenAI evidence unless `python -B scripts/dev.py openai-live` passed in an API-key environment

If live mode fails, document the failure as environment-dependent and keep the release claim anchored to the local deterministic gates.

## Troubleshooting Sequence

Use this order:

```bash
git status --short --branch
python -B scripts/dev.py model-gateway-safety
python -B scripts/dev.py safety
python -B scripts/dev.py openai-live
```

If a code or docs change was made while troubleshooting, finish with:

```bash
python -B scripts/dev.py quality
```

Use `docs/command_output_troubleshooting_map.md` when a broader gate fails. Do not hide a failure by loosening safety checks, logging secrets, or making the optional provider the default path.
