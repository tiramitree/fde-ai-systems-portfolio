# Summary

Describe the change.

## Checks

- [ ] `python -B scripts\check_health.py`
- [ ] `python -B scripts\run_all_evals.py`
- [ ] `python -B scripts\smoke_test_demo_flows.py`
- [ ] `python -B scripts\public_safety_scan.py`
- [ ] `python -B scripts\check_dependency_surface.py`
- [ ] Docs updated where needed

## Safety Review

- [ ] Permission checks are preserved.
- [ ] Approval gates are preserved.
- [ ] No secrets, local files, private user data, or account credentials are read, logged, or uploaded.
- [ ] Dependency surface is intentional; no hidden pip, npm, CDN, or unpinned Docker dependency was added.
- [ ] Eval or CI failures are not hidden.
- [ ] No required OpenAI API dependency was added to the local demo path.
- [ ] New risky behavior has eval coverage.
