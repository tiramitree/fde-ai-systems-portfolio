# Scenario Data Integrity

The repository uses small fictional datasets so the demos are understandable, repeatable, and safe to publish. The scenario data integrity gate makes sure those datasets keep supporting the claims made in the README and release materials. The browser scenario draft panels read these seed snapshots and store edits only in browser localStorage.

Run it with:

```bash
python -B scripts/dev.py scenario-data
```

## What It Checks

Project 1 checks:

- demo users include employee, manager, and admin roles
- all users are scoped to the fictional `acme` tenant
- document ids are unique
- document `source_url` values use the fictional `internal://` scheme
- confidential documents are not visible to the employee role
- confidential documents remain visible to manager and admin roles
- the unsafe vendor note remains present as a retrieved-content injection fixture
- eval ids are unique and consistently formatted
- eval user ids and cited/forbidden document ids all point to existing seed data
- answer evals require citations
- security-event evals include injection, exfiltration, or override markers

Project 2 checks:

- demo users include investigator and supervisor roles
- policy, product, seller, listing, and case ids are unique
- policy fixtures describe approval behavior
- active recalls include recall ids and hazards
- listings point to existing sellers and products
- at least one active listing exists for an actively recalled product
- cases point to existing sellers and products
- eval ids are unique and consistently formatted
- eval users, cases, policies, and intents point to existing seed data
- every eval forbids direct side effects
- approval evals require a blocked action before approval
- refusal evals contain a bypass/override marker or a non-supervisor approval attempt

Project 3 checks:

- demo users include reliability lead and product manager roles
- release, incident, runbook, and eval case ids are unique
- eval runs point to existing releases
- eval run metrics match the number of cases
- incidents point to existing releases
- incident severities and statuses stay within the expected operational vocabulary
- incident runbook ids and linked eval case ids point to existing seed data
- eval cases point to existing users, releases, and incidents
- blocked release cases include remediation phrases

The gate also scans the seed and eval JSON for local paths, private artifacts, obvious secret markers, and personal identifiers that should never appear in public fixtures.

The browser-local scenario draft surface depends on this same data contract:

- `/api/scenario` exposes only allowlisted fictional seed and eval files.
- runtime state files are not part of the scenario snapshot.
- drafts are copied/exported from the browser and stored in browser `localStorage`, not written back to repository JSON.
- JSON seed files remain the source of truth for evals and reset behavior.

## Technical Review Framing

The data is deliberately small, but it is not arbitrary. Each fixture exists to demonstrate a production invariant: permission filtering before generation, citation-backed answers, abstention, retrieved-content injection handling, deterministic tools, approval gates, blocked side effects, and release triage. The integrity gate prevents future edits from making the demo story inconsistent or accidentally publishing private artifacts, while the scenario draft UI makes the fictional data inspectable and copyable without mutating it.
