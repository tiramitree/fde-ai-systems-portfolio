# Trace-To-Eval Workflow

Production AI systems need a loop from observed behavior back into regression coverage. This repository keeps that loop local-first and reviewable:

```text
runtime trace
  -> audit / approval / release evidence
  -> trace-to-eval candidate artifact
  -> human review
  -> reviewed dataset ledger
  -> checked-in golden eval
  -> CI quality gate
```

The workflow does not automatically mutate checked-in eval fixtures. It exports review candidates under `out/`, which is ignored by Git.

Candidate JSON also passes through `public_trace_export_redaction_v1` before it is written. This keeps the trace-to-eval loop useful for review while avoiding direct promotion of common email, phone, secret-like, private ID, or local path markers from runtime traces. Verify the redaction boundary with:

```bash
python -B scripts/dev.py trace-redaction
```

## Commands

Generate canonical trace evidence, then export candidates:

```bash
python -B scripts/dev.py replay
python -B scripts/dev.py trace-to-eval
```

Validate the candidate exporter and expected coverage:

```bash
python -B scripts/dev.py trace-to-eval-check
python -B scripts/dev.py reviewed-eval-ledger
```

Generated files:

```text
out/trace_eval_candidates.json
out/trace_eval_candidates.md
```

Each JSON candidate carries review metadata:

- `review.owner_role`: the maintainer role expected to inspect the candidate.
- `review.default_disposition`: starts as `undecided`.
- `review.allowed_dispositions`: `promote_to_golden_eval`, `needs_fixture_edit`, or `reject_noisy_or_duplicate_trace`.
- `review.promotion_target`: the checked-in eval fixture path to edit after review.
- `review.regression_schedule`: `nightly` for high/critical risks and `release-gate` for medium risks.
- `review.promotion_requirements`: the checks that must pass before promotion.

The checked-in reviewed dataset ledger lives at `docs/reviewed_eval_dataset_ledger.json`. It records the active golden fixture for each project, reviewer role, candidate categories, current case count, regression schedule, and commands that must pass before a trace candidate is promoted. The ledger is verified by:

```bash
python -B scripts/dev.py reviewed-eval-ledger
```

Nightly regression is scheduled in `.github/workflows/nightly-regression.yml` with read-only repository permissions. The workflow checks the ledger, regenerates replay traces, exports trace-to-eval candidates, validates those candidates, runs Project 1 retrieval metrics, runs all golden evals, and verifies public metric claims.

## Candidate Types

Project 1 candidates:

- `p1_permission_abstain`: inaccessible evidence caused abstention and recorded denied-evidence count.
- `p1_prompt_injection_abstain`: unsafe override, exfiltration, or retrieved-content injection caused abstention with a security event.
- `p1_grounded_citation_answer`: cited answer can become a grounding, citation-shape, chunk-span, sentence evidence-span, and source-lifecycle regression case.

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
- set a human disposition before changing source fixtures
- update `docs/reviewed_eval_dataset_ledger.json` if the target fixture, case count, owner, candidate category, or regression schedule changes
- route Project 1 candidates to the knowledge-safety reviewer, Project 2 candidates to the agent-governance reviewer, and Project 3 candidates to the release-reliability reviewer
- rerun `python -B scripts/dev.py scenario-data`, `python -B scripts/dev.py reviewed-eval-ledger`, `python -B scripts/dev.py evals`, `python -B scripts/dev.py retrieval-metrics`, `python -B scripts/dev.py claims`, and `python -B scripts/dev.py quality`

Do not promote runtime-only IDs, local paths, generated logs, private endpoints, tokens, or environment dumps into source files.

## Industrial Framing

This is the local version of an eval-ops loop. In production, traces from a collector, audit store, or incident console would feed a reviewed dataset workflow. The same invariant remains: observed failures and high-risk decisions become regression coverage only after review, so quality improves without letting noisy or sensitive runtime data leak into public fixtures. Automated redaction is a guardrail, not a replacement for human review before a candidate becomes a checked-in golden eval.
