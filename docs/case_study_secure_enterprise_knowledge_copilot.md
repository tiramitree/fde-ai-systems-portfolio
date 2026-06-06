# Case Study: Secure Enterprise Knowledge Copilot

## Problem

Enterprise employees need answers from internal policies, but a normal RAG assistant creates risk:

- users may retrieve documents they should not access
- answers may cite stale or unsupported evidence
- retrieved documents may contain prompt injection
- teams need traces and audit records for debugging and review

## Design Goal

Build a knowledge copilot that answers only from accessible evidence, cites sources, abstains when evidence is missing, and records enough trace/audit data to debug failures.

## Architecture

```text
User question
  -> user role and tenant
  -> retrieve candidate chunks
  -> filter by role before evidence assembly
  -> remove unsafe retrieved instructions
  -> answer with citations or abstain
  -> write trace and audit
  -> eval gate
```

## Key Product Behaviors

- Alice can answer general HR and security policy questions.
- Alice cannot answer confidential finance retention questions.
- Morgan can answer finance retention questions because manager role has access.
- Unsupported questions abstain instead of fabricating.
- Prompt-injection content is treated as data and excluded.

## Why This Is Not A Basic RAG Demo

Basic RAG usually demonstrates retrieval and answer generation.

This project demonstrates enterprise control surfaces:

- permission filtering before model context
- citation enforcement
- abstention
- prompt-injection handling
- trace viewer
- audit log
- regression evals

## Evaluation Strategy

The golden eval suite checks:

- required citations
- forbidden confidential citations
- abstention for unsupported questions
- prompt-injection handling
- permission-blocked evidence

Latest verified result:

```text
13/13 evals passed
unsafe_leak_failures = 0
```

## Design Review Answer

If asked why this is useful when real companies have existing knowledge systems:

> Existing search systems usually do not provide grounded conversational answers with policy-aware abstention, traceable evidence, and eval gates. The key is not replacing search. The key is making retrieval, answer generation, and governance inspectable enough to deploy in an enterprise workflow.

## Production Upgrade

Replace the local JSON store and keyword retrieval with:

- identity provider integration
- PostgreSQL with row-level security
- pgvector and hybrid retrieval
- document parser pipeline
- queue-based ingestion
- OpenAI Responses API structured output
- OpenTelemetry traces
- CI eval gates
