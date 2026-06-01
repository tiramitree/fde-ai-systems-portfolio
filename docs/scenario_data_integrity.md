# Scenario Data Integrity

The portfolio uses small fictional datasets so the demos are understandable, repeatable, and safe to publish. The scenario data integrity gate makes sure those datasets keep supporting the claims made in the README and interview materials.

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

The gate also scans the seed and eval JSON for local paths, private artifacts, obvious secret markers, and personal identifiers that should never appear in public fixtures.

## Interview Framing

The data is deliberately small, but it is not arbitrary. Each fixture exists to demonstrate a production invariant: permission filtering before generation, citation-backed answers, abstention, retrieved-content injection handling, deterministic tools, approval gates, and blocked side effects. The integrity gate prevents future edits from making the demo story inconsistent or accidentally publishing private artifacts.
