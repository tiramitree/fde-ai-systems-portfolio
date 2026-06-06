# Trace-To-Eval Workflow

Production AI systems need a loop from observed behavior back into regression coverage. This repository keeps that loop local-first and reviewable:

```text
runtime trace
  -> audit / approval / release evidence
  -> trace-to-eval candidate artifact
  -> human review
  -> checked-in golden eval
  -> CI quality gate
```

The workflow does not automatically mutate checked-in eval fixtures. It exports review candidates under `out/`, which is ignored by Git.

## Commands

Generate canonical trace evidence, then export candidates:

```bash
python -B scripts/dev.py replay
python -B scripts/dev.py trace-to-eval
```

Validate the candidate exporter and expected coverage:

```bash
python -B scripts/dev.py trace-to-eval-check
```

Generated files:

```text
out/trace_eval_candidates.json
out/trace_eval_candidates.md
```

## Candidate Types

Project 1 candidates:

- `p1_permission_abstain`: inaccessible evidence caused abstention and recorded denied-evidence count.
- `p1_prompt_injection_abstain`: unsafe override, exfiltration, or retrieved-content injection caused abstention with a security event.
- `p1_grounded_citation_answer`: cited answer can become a grounding and citation-shape regression case.

Project 2 candidates:

- `p2_side_effect_requires_approval`: external side effect was converted into an approval request.
- `p2_governance_bypass_refusal`: approval/logging bypass attempt was refused without side effects.

Project 3 candidates:

- `p3_release_block_from_failed_eval`: failed eval evidence caused rollout blocking.
- `p3_monitor_only_eval_signal`: lower-risk eval evidence stayed monitor-only.

## Review Rules

Before promoting a candidate into a checked-in eval fixture:

- verify the seed data is fictional and public-safe
- keep the expected contract minimal and tied to one durable invariant
- preserve existing unsafe counters at zero
- copy only the suggested input and expected behavior, not generated trace IDs
- rerun `python -B scripts/dev.py scenario-data`, `python -B scripts/dev.py evals`, `python -B scripts/dev.py claims`, and `python -B scripts/dev.py quality`

Do not promote runtime-only IDs, local paths, generated logs, private endpoints, tokens, or environment dumps into source files.

## Industrial Framing

This is the local version of an eval-ops loop. In production, traces from a collector, audit store, or incident console would feed a reviewed dataset workflow. The same invariant remains: observed failures and high-risk decisions become regression coverage only after review, so quality improves without letting noisy or sensitive runtime data leak into public fixtures.
