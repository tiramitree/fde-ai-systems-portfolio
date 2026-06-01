# Summary

Describe the change.

## Checks

- [ ] `python -B scripts\check_health.py`
- [ ] `python -B scripts\run_all_evals.py`
- [ ] `python -B scripts\smoke_test_demo_flows.py`
- [ ] Docs updated where needed

## Safety Review

- [ ] Permission checks are preserved.
- [ ] Approval gates are preserved.
- [ ] No required OpenAI API dependency was added to the local demo path.
- [ ] New risky behavior has eval coverage.

