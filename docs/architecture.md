# SOCAI Platform Architecture

## Overview

SOCAI is an AI-native Managed Security Operations platform designed to automate
SOC delivery using:

- Wazuh (Telemetry + SIEM backbone)
- OpenSearch (Data storage + analytics)
- TheHive (Incident case management)
- MISP (Threat intelligence)
- AI Orchestrator Layer (SOC intelligence automation)
- Customer Portal + Analyst Workbench

The platform goal is to reduce manual SOC effort by automating:
- alert triage
- enrichment
- risk scoring
- reporting
- detection improvement feedback loops

---

## High Level Architecture

Security Telemetry Sources
- Endpoints (Wazuh agents)
- Cloud logs (AWS / Azure / GCP)
- SaaS logs (Okta / M365 / Google Workspace)
- Network devices / WAF / CDN
- Vulnerability scanners
- EDR platforms

↓

Wazuh Manager Cluster
- Log ingestion
- Rule evaluation
- Alert generation

↓

OpenSearch Cluster
- Alert storage
- Query analytics
- Dashboard datasets

↓

SOCAI AI Orchestrator Platform
Core responsibilities:
- Alert normalization
- IOC extraction
- Enrichment pipelines
- MITRE mapping inference
- Risk scoring
- Alert clustering
- Case generation logic
- Detection tuning intelligence
- Report automation

↓

Case Management Layer (TheHive)
- Incident lifecycle
- Task tracking
- Analyst collaboration
- Evidence management

↓

Threat Intelligence Layer (MISP)
- IOC enrichment
- Campaign tracking
- Cross-customer intelligence
- Feed ingestion

↓

User Interfaces
- Analyst Workbench
- Customer Portal
- Executive dashboards
- Automation health dashboards

---

## Core Design Principles

- Multi-tenant by design
- Automation-first SOC workflows
- AI assists decision making (does not replace approval)
- No destructive containment without approval workflow
- Modular architecture (agent-driven)
- API-first platform
- Observability and auditability built-in
- Security controls enforced at every layer

---

## Deployment Model

Primary deployment model:
- Docker Compose (single VM lab / early customers)
- Kubernetes (future scale)

Supported environments:
- Linux server preferred
- Windows supported for local dev

---

## Key Integrations

- Wazuh API
- OpenSearch API
- TheHive API
- MISP API
- Threat intel APIs
- Cloud provider APIs
- Endpoint agent deployment scripts

---

## Future Architecture Evolution

- Horizontal scaling ingestion layer
- Event streaming (Kafka / Redpanda)
- ML anomaly detection pipelines
- Cross-tenant intelligence graph
- Predictive risk scoring engine
- Safe response orchestration engine
