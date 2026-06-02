# Demo Script

1. Start the app with `python -B app.py --reset --port 8780`.
2. Open `http://127.0.0.1:8780`.
3. Show `rel-2026-06-01` as a canary release.
4. Select `inc-2026-014` and run triage.
5. Explain why the release is blocked:
   - unauthorized-answer incident
   - linked failed evals
   - rollback remediation
   - trace and audit evidence
6. Select `inc-2026-015` and run triage.
7. Explain why this is monitored rather than blocked:
   - latency regression
   - no unsafe leak or side-effect boundary failure
8. Run evals and show the release-blocking assertions.
