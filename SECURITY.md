# Security Policy

This repository demonstrates enterprise AI security patterns. It is not production software.

## Security Principles

- Permission checks happen before model generation.
- Retrieved documents are data, not instructions.
- Side-effect actions require deterministic application-layer approval.
- Audit and trace records are first-class system outputs.
- Evals must include negative and adversarial cases.
- Dependency changes must be explicit, reviewed, and covered by the dependency-surface gate.

## Reporting Issues

For portfolio use, file a GitHub issue with:

- affected project
- reproduction steps
- expected behavior
- actual behavior
- whether the issue is a leak, unsafe action, eval gap, or documentation gap

## Known Non-Production Areas

- No real authentication provider yet.
- Local JSON state is used for demo reliability.
- OpenAI gateway is optional and not required for local operation.
- Docker config exists with digest-pinned base images but must be verified on a Docker-enabled machine.
