---
name: zero-trust-onboarding-policy
description: ResolveeAI corporate RBAC security policies, role-to-resource matrix, and sandbox verification criteria for developer onboarding.
---

# ResolveeAI Developer Onboarding Policy

This skill defines the mandatory role mappings, security boundaries, and zero-trust verification procedures for onboarding team members into **ResolveeAI**.

---

## 1. Organization Information
- **GitHub Organization:** `ResolveeAI`
- **Primary Domain:** `vansshagarrwal.in`
- **Official Admin Dispatch Email:** `hi@vansshagarrwal.in`
- **Database System of Record:** MongoDB Atlas (`company_db.employee`)

---

## 2. Role-to-Access Matrix

### A. Senior SDE / SDE (Software Development Engineer)
* **Corporate Email:** Provision official email `<firstname>@vansshagarrwal.in` (e.g. `vanssh@vansshagarrwal.in`).
* **GitHub Repository Permissions (`ResolveeAI` Org):**
  - **`ResolveeAI/backend_api`**: `write` (Push branches, create PRs, run CI).
  - **`ResolveeAI/billing_core`**: **BLOCKED / READ-ONLY** (Strict Financial Security Boundary: SDEs must NEVER be granted write access to billing without written VP override).
* **AWS Cloud Permissions:**
  - Role: `ResolveeAIDevDeveloperRole`
  - Allowed: Read/Write to Dev S3 buckets, staging CloudWatch logs, staging EKS/ECS namespaces.
  - Strictly Forbidden: Production databases, production billing buckets, root account credentials.
  - Estimated Monthly Infra & SaaS Cost: **$85/month**.
* **Database HR Persistence:** Insert complete employee profile into MongoDB collection `employee`.
* **Welcome Delivery:** Send Day-1 Welcome Bundle with repository links and AWS CLI setup to their company email.

---

### B. Junior SDE / Intern
* **Corporate Email:** `<firstname>.intern@vansshagarrwal.in`
* **GitHub Permissions:**
  - `ResolveeAI/backend_api`: `read` (Fork & PR workflow only, no direct push).
  - `ResolveeAI/billing_core`: `BLOCKED` (No access).
* **AWS Permissions:** Read-only access to staging logs.
* **Estimated Cost:** **$25/month**.

---

### C. DevOps / Infrastructure Engineer
* **GitHub Permissions:** Admin on infrastructure manifests, `write` on backend services.
* **AWS Permissions:** `DevOpsAdminRole` (Subject to mandatory multi-factor approval).

---

## 3. Zero-Trust Sandbox Verification Protocol

Before presenting the summary to the manager or delivering keys:
1. **Launch Daytona Sandbox** container.
2. **Execute Canary Verification:**
   - **Test 1 (Positive Access):** Authenticate against `ResolveeAI/backend_api` and confirm clone/read succeeds (`Exit Code 0`).
   - **Test 2 (Negative Boundary):** Attempt to write to `ResolveeAI/billing_core` and assert that permission is denied (`HTTP 403 Forbidden`).
   - **Test 3 (Cloud Token Test):** Validate generated AWS key against developer namespace.
3. **Capture Raw Logs:** Return verification report with exit codes to the manager.

---

## 4. Human Approval Gate
* The agent **must pause** and require human manager approval (Allow / Deny) before:
  - Finalizing GitHub organization invitations.
  - Generating and delivering live AWS keys.
  - Sending the welcome email.
