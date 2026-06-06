# Threat Model

## Assets

- Confidential documents.
- Ingested and synced document sources, GitHub issue/PR source URLs, source hashes, connector names, external IDs, ACL source metadata, ACL snapshot versions, source permission IDs, permission drift evidence, sync cursors, ingestion job IDs, idempotency keys, retry parent links, and dead-letter evidence.
- User identity and role.
- Retrieved evidence.
- Model prompts and outputs.
- Audit logs and traces.

## Main Risks

1. User receives citations from documents they cannot access.
2. Retrieved document contains prompt injection and tells the model to leak data.
3. The system fabricates an answer when no accessible evidence exists.
4. Logs contain sensitive data without access controls.
5. A non-admin user, poisoned source, or mis-scoped connector sync adds searchable content.
6. A retrieval or prompt change silently degrades quality.

## Current Controls

- Tenant and role filter before retrieval scoring and answer assembly.
- Admin-only ingestion, source sync, GitHub connector intake, and ingestion jobs with tenant, classification, role, duplicate, parser metadata, source hash, connector metadata, GitHub owner/repo validation, issue/PR source URLs, ACL source, ACL snapshot fail-closed validation, source permission ID, permission drift, sync cursor, job idempotency, sanitized input summary, retry parent, dead-letter, and chunk-count validation.
- Forbidden citation checks in evals.
- Prompt injection pattern detection in retrieved content.
- Abstention when no accessible evidence clears the threshold.
- Trace IDs for debugging retrieval score breakdowns and answer behavior.
- Audit events for ingestion parser warnings, source sync completion, GitHub connector sync, ingestion job completion, ingestion job dead-letter, permission drift, query, citation, abstention, and security-event counts.

## Production Controls To Add

- Real auth and signed session tokens.
- Connector-backed ingestion with source user/group permission sync, parser isolation, parser version pinning, checkpoint recovery, and malware scanning.
- Row-level security in PostgreSQL.
- PII redaction in logs.
- Policy-as-code for tool and retrieval permissions.
- Human review for sensitive answer categories.
- Adversarial eval set from production failures.
