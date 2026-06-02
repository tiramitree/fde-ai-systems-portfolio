# ADR 0001: Local-First Reference Runtime

Status: accepted

## Context

The repository needs to be usable by GitHub readers and technical reviewers without API keys, Docker, cloud credentials, or paid services.

## Decision

The default runtime uses Python standard library services, static frontend assets, and local JSON state.

Optional adapters are documented for:

- OpenAI Responses API
- OpenAI Agents SDK
- PostgreSQL / pgvector
- Docker Compose
- OpenTelemetry

## Consequences

Benefits:

- fast local setup
- no paid API dependency
- deterministic eval behavior
- easy local review demo
- easy CI verification

Tradeoffs:

- not a production storage layer
- no real auth provider
- no real vector database by default
- Docker and OpenAI live modes require external verification

## Design Review Explanation

The goal is not to claim production readiness. The goal is to demonstrate production control boundaries in a runnable form: permissions, approval gates, traces, audit logs, and evals.

