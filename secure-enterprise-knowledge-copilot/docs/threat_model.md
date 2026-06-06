# Threat Model

## Assets

- Confidential documents.
- Ingested document sources and source hashes.
- User identity and role.
- Retrieved evidence.
- Model prompts and outputs.
- Audit logs and traces.

## Main Risks

1. User receives citations from documents they cannot access.
2. Retrieved document contains prompt injection and tells the model to leak data.
3. The system fabricates an answer when no accessible evidence exists.
4. Logs contain sensitive data without access controls.
5. A non-admin user or poisoned source adds searchable content.
6. A retrieval or prompt change silently degrades quality.

## Current Controls

- Tenant and role filter before answer assembly.
- Admin-only ingestion with tenant, classification, role, duplicate, source hash, and chunk-count validation.
- Forbidden citation checks in evals.
- Prompt injection pattern detection in retrieved content.
- Abstention when no accessible evidence clears the threshold.
- Trace IDs for debugging retrieval and answer behavior.
- Audit events for ingestion, query, citation, abstention, and security-event counts.

## Production Controls To Add

- Real auth and signed session tokens.
- Connector-backed ingestion with source permission sync, parser isolation, and malware scanning.
- Row-level security in PostgreSQL.
- PII redaction in logs.
- Policy-as-code for tool and retrieval permissions.
- Human review for sensitive answer categories.
- Adversarial eval set from production failures.
