---
name: zero-trust-onboarding-policy
description: Corporate RBAC security policies, role-to-resource matrix, and sandbox verification criteria for onboarding new team members.
---

# Enterprise Developer Onboarding Policy

This skill defines the mandatory role mappings, security boundaries, and verification procedures for developer onboarding.

## 1. Role-to-Access Matrix

### Senior Backend Engineer
- **GitHub Repos:**
  - `org/backend-api` (Permission: `write`)
  - `org/auth-service` (Permission: `write`)
  - `org/infrastructure` (Permission: `read`)
  - `org/billing-core` (Permission: `read` only — NO write access without VP approval)
- **Cloud / IAM (Azure / AWS):**
  - Dev/Staging Kubernetes cluster namespace access
  - Read access to Dev cloud storage buckets
  - **FORBIDDEN:** Direct access to Production DB credentials or Production secrets.
- **Estimated Seat Cost:** $85/month (GitHub Enterprise + AWS Dev IAM + Datadog dev seat).

### Junior / Intern Engineer
- **GitHub Repos:** Read/Triage on all service repos, Fork/PR workflow.
- **Cloud:** Read-only access to Staging logs.

---

## 2. Zero-Trust Verification Protocol (Sandbox Execution)

Before requesting manager approval or delivering credentials:
1. **Spin up temporary sandbox execution environment.**
2. **Execute Canary Verification:**
   - Test 1 (Positive Repo Check): Attempt to authenticate and read branches from `org/backend-api`.
   - Test 2 (Negative Boundary Check): Attempt to write to `org/billing-core` — must receive `403 Forbidden` or permission denied.
   - Test 3 (Cloud Token Check): Verify identity token against staging namespace.
3. **Capture Evidence Matrix:** Return a clean PASS/FAIL report for each test.
4. **Teardown Sandbox.**

---

## 3. Approval Gate Thresholds
- **Human Approval is strictly REQUIRED** if:
  - Any `write` access is provisioned.
  - Any cloud IAM role is assigned.
  - Estimated monthly cost exceeds $50/month.
- **Immediate Rejection / Warning** if:
  - Access to `production-*` resources is requested without explicit compliance tickets.
