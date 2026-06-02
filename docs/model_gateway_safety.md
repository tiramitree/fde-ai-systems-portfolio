# Model Gateway Safety

The repository runs locally by default. OpenAI mode is an optional gateway, not a security boundary and not a required dependency for the demo.

Run the model gateway safety gate with:

```bash
python -B scripts/dev.py model-gateway-safety
```

With a real API key, run the live mode proof with:

```bash
python -B scripts/dev.py openai-live
```

## Safety Contract

The gate verifies that:

- `.env.example` keeps `OPENAI_API_KEY` blank
- both model-facing project routes default to local mode
- Docker Compose passes `OPENAI_API_KEY` only as an optional environment value
- `OPENAI_API_KEY` references stay in an explicit allowlist
- both model gateways use the Responses API endpoint
- gateway calls use structured JSON schema outputs
- provider/router environment variables must explicitly opt in to OpenAI mode
- failed API calls, malformed responses, or timeouts return `None` and fall back to deterministic local behavior
- the gateways do not print, log, shell out, dynamically execute code, or re-raise API/parse failures
- the live check requires OpenAI mode to be observed in API responses and still preserve grounded answers, approval requests, and side-effect blocking

## Boundary Statement

OpenAI mode changes only the model-facing part of each workflow:

- Project 1 can ask the model to improve grounded answer wording after permission filtering, unsafe-content filtering, citation selection, and abstention logic already ran.
- Project 2 can ask the model to classify intent before deterministic tool permissions, approval gates, and side-effect controls run.

The model never becomes the authority for permissions, evidence access, approval execution, audit logging, or eval success.

## Technical Review Framing

Use this answer when challenged on API keys or model dependency:

```text
The verified default path is local and deterministic. The optional OpenAI gateway is opt-in through environment variables, the API key stays outside the repo, and failures return None so the app falls back to local behavior. Permissions and side-effect authorization are enforced before or after the model call in application code, so changing the model provider does not weaken the security invariants. When a key is available, `python -B scripts/dev.py openai-live` proves the model-backed path was actually used.
```
