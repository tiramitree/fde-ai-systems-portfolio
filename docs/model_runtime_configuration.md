# Model Runtime Configuration

Date reviewed: 2026-06-01

This portfolio runs locally by default. The OpenAI path is optional and intentionally limited to model-facing work:

- Project 1: grounded answer wording after permission filtering, unsafe-content filtering, citation selection, and abstention logic.
- Project 2: intent classification before deterministic tool permission and approval checks.

The model is not the security boundary.

See [Model Gateway Safety](model_gateway_safety.md) for the gate that verifies OpenAI mode stays opt-in, API key references remain constrained, structured outputs are required, and gateway failures fall back to local behavior.

## Default Optional Model

The default optional model is:

```text
OPENAI_MODEL=gpt-5.2
```

Reason:

- OpenAI's current model guide lists `gpt-5.2` as the best model for coding and agentic tasks across industries.
- OpenAI's GPT-5.2 guide recommends the Responses API for reasoning, tool-calling, and multi-turn use cases.
- The portfolio keeps the local deterministic mode as the verified default so demos do not depend on paid API access.

References:

- https://platform.openai.com/docs/models
- https://platform.openai.com/docs/guides/latest-model
- https://platform.openai.com/docs/api-reference/responses
- https://platform.openai.com/docs/guides/structured-outputs

## Environment Variables

```powershell
$env:OPENAI_API_KEY="..."
$env:OPENAI_MODEL="gpt-5.2"
$env:OPENAI_REASONING_EFFORT="medium"
$env:OPENAI_TEXT_VERBOSITY="low"
$env:COPILOT_MODEL_PROVIDER="openai"
$env:OPS_AGENT_MODEL_ROUTER="openai"
```

With a real key, run the live proof:

```powershell
python -B scripts/dev.py openai-live
```

That command starts both apps on isolated local ports with OpenAI mode enabled. It requires Project 1 to report `model_provider=openai`, Project 2 to report `model_router=openai`, and both workflows to keep their normal safety behavior.

Supported reasoning effort values:

```text
none, low, medium, high, xhigh
```

Supported verbosity values:

```text
low, medium, high
```

## Project 1 Defaults

Project 1 uses:

```text
OPENAI_REASONING_EFFORT=medium
OPENAI_TEXT_VERBOSITY=low
```

Rationale:

- Medium effort is a reasonable default for grounded enterprise answers where precision matters.
- Low verbosity keeps the generated answer concise because citations and evidence are already shown by application code.
- Structured output forces the response into an answer/confidence/missing-evidence shape.

## Project 2 Defaults

Project 2 uses:

```text
OPENAI_REASONING_EFFORT=low
OPENAI_TEXT_VERBOSITY=low
```

Rationale:

- Intent routing should be fast and constrained.
- The model returns only an enum intent.
- Approval decisions and side effects remain deterministic application behavior.

## Interview Positioning

Use this wording:

```text
I keep local deterministic mode as the verified default, then expose an optional OpenAI Responses API path for the model-facing part of each workflow. I tune model, reasoning effort, verbosity, and structured outputs through environment variables, but I do not move permissions or side-effect authorization into the model. When a key is available, `python -B scripts/dev.py openai-live` proves both apps actually used OpenAI mode while preserving citations, approvals, and side-effect blocking.
```
