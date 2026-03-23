# SOCAI Development Rules

## Core Philosophy

- Keep tasks small and controlled
- Automation-first architecture
- Security-reviewed implementation
- Documentation always updated
- One task = one pull request

---

## Coding Standards

- Python 3.11+
- FastAPI for backend APIs
- PostgreSQL for platform metadata
- OpenSearch for alert analytics
- Structured logging mandatory
- Config via environment variables
- No hardcoded secrets

---

## Architecture Discipline

- API-first design
- Modular package layout
- Avoid tight coupling between agents
- Separate AI reasoning layer from SIEM ingestion
- All enrichment must be idempotent

---

## AI-Generated Code Policy

- AI output is draft until reviewed
- Security sensitive logic must be manually validated
- Prefer simple implementation first
- Avoid premature optimization
- Avoid large auto-generated files without tests

---

## Git Workflow

- Feature branch per module task
- Mandatory PR review before merge
- Descriptive commit messages
- Update documentation in same PR
- Maintain CHANGELOG

---

## Security Guardrails

- No automatic containment actions
- All response actions require approval workflow
- Audit logs required for all automation decisions
- Tenant isolation must be enforced
- Input validation mandatory on APIs

---

## Testing Expectations

- Unit tests for core logic
- Integration tests for connectors
- Synthetic alert test datasets
- Manual SOC workflow validation

---

## Observability Requirements

- Health endpoints for all services
- Metrics export capability
- Structured error reporting
- Automation decision logging
