# Summary

Describe the change.

## Checks

- [ ] `python -B scripts\check_health.py`
- [ ] `python -B scripts\run_all_evals.py`
- [ ] `python -B scripts\smoke_test_demo_flows.py`
- [ ] `python -B scripts\public_safety_scan.py`
- [ ] Docs updated where needed

## Safety Review

- [ ] Permission checks are preserved.
- [ ] Approval gates are preserved.
- [ ] No secrets, local files, private user data, or account credentials are read, logged, or uploaded.
- [ ] Eval or CI failures are not hidden.
- [ ] No required OpenAI API dependency was added to the local demo path.
- [ ] New risky behavior has eval coverage.
