# PR Review Security Gate

Run:

```bash
python -B scripts/dev.py pr-policy
```

Public repositories receive untrusted code. `python -B scripts/dev.py pr-triage` inspects live open PRs, while this gate protects the review policy itself. It fails if the triage script, runbook, maintainer policy, or PR template loses the checks needed before approving workflows, running contributor code, or merging.

## What It Protects

The gate verifies that `scripts/review_open_prs.py` still flags:

- high-impact files such as workflows, safety scans, quality gates, model gateway files, retrieval, answering, and tool-execution code
- dependency and runtime-adjacent files such as package manifests, Dockerfiles, `.gitignore`, eval cases, and model gateways
- binary and executable file types
- secret-like markers and private local path markers
- shell execution, destructive filesystem calls, dynamic code execution, outbound network behavior, environment access, and dependency-install commands

It also verifies that:

- the PR review runbook still says to read the diff before running code
- strict triage mode is documented
- the maintainer policy still calls out secrets, unrelated links, obfuscated code, weakened safety controls, and GitHub Actions review
- the PR template still asks contributors to preserve permissions, approvals, dependency policy, local demo behavior, eval coverage, and CI visibility

## Review Rule

For an external PR:

1. Run `python -B scripts/dev.py pr-triage`.
2. Read the diff before running code.
3. If high-risk findings appear, do not run contributor code until the diff is understood.
4. Run `python -B scripts/dev.py pr-policy`, `python -B scripts/dev.py governance`, `python -B scripts/dev.py workflow-security`, `python -B scripts/dev.py safety`, and `python -B scripts/dev.py verify` before merge.
5. Merge only if the change improves the portfolio without weakening permissions, approvals, audit, traces, evals, dependency posture, or local reproducibility.

## Interview Framing

Use this answer:

```text
I treat public PRs as untrusted input. The live triage command inspects open PRs, and the PR-policy gate protects the triage rules, runbook, maintainer policy, and PR template from being quietly weakened. That means review process is itself tested, not just documented.
```
