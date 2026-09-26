# 🛡️ ResolveeAI: Autonomous Zero-Trust Employee Lifecycle Agent

[![TrueForge Powered](https://img.shields.io/badge/Powered%20By-TrueForge%20%7C%20TrueFoundry-blueviolet?style=for-the-badge)](https://truefoundry.com)
[![FastMCP](https://img.shields.io/badge/Protocol-Model%20Context%20Protocol%20(MCP)-blue?style=for-the-badge)](https://modelcontextprotocol.io)
[![Sandbox](https://img.shields.io/badge/Verification-Daytona%20Cloud%20Sandbox-brightgreen?style=for-the-badge)](https://daytona.io)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

> **Built for the "Agents That Act: TrueFoundry × Polaris Hackathon"**  
> An autonomous AI security agent that provisions, verifies, persists, and revokes developer credentials in real time across **GitHub Organizations**, **AWS IAM**, **Zoho Directory**, and **MongoDB Atlas** with Daytona Sandbox canary validation and zero-trust RBAC.

---

## ⚡ The Problem: IT & Security Lifecycle Fragility
- **Manual Onboarding Bottlenecks:** Provisioning corporate emails, IAM access, repo permissions, and database records typically requires 3–5 business days across disjointed IT tickets.
- **Overprivileged Blanket Access:** Developers are often given organization-wide write or admin access because granular configuration takes too much time.
- **Zombie Credentials & Leaky Offboarding:** According to Ponemon Institute research, **83% of former employees retain access** to at least one corporate system after leaving, creating massive security and compliance vulnerabilities.

---

## 🚀 The Solution: ResolveeAI Autonomous Governance
ResolveeAI operates as an autonomous pair-programmer and security officer on **TrueForge**. Given a simple prompt (e.g. `"setup profile for Vanssh joining as SDE"` or `"offboard Algo"`), the agent autonomously orchestrates the complete lifecycle:

```mermaid
flowchart TD
    User([Manager Prompt]) --> TF[TrueForge Agent]
    
    subgraph "Onboarding Lifecycle"
        TF --> Z1[1. Provision Zoho Mailbox]
        Z1 --> Z2[Generate Temp Password]
        TF --> GH1[2. Issue GitHub Access]
        GH1 --> GH2[Allowed: ResolveeAI/backend_api]
        GH1 --> GH3[Blocked: ResolveeAI/billing_core]
        TF --> AWS1[3. Generate Scoped AWS IAM Keys]
        TF --> SBX[4. Daytona Canary Sandbox Verification]
        SBX --> HIL[5. Human-in-the-Loop Audit Gate]
        HIL --> DB1[6. Persist to MongoDB Atlas]
        DB1 --> EM1[7. Dispatch Zoho Welcome Email]
    end

    subgraph "Offboarding Lifecycle (Zero-Zombie)"
        TF --> O1[1. Disambiguation & Ambiguity Check]
        O1 --> O2[2. Revoke GitHub Org & Repo Collaborators]
        O1 --> O3[3. Deactivate AWS IAM Keys & Sessions]
        O1 --> O4[4. Suspend Zoho Corporate Mailbox]
        O1 --> O5[5. Update MongoDB Status to OFFBOARDED]
        O1 --> O6[6. Send Leadership Audit Certificate]
    end
```

---

## 🌟 Key Highlights & Differentiators

### 1. 🛡️ Real-Time Zero-Trust RBAC Policy Enforcement
- **Backend / SDE:** Write access to `ResolveeAI/backend_api`.
- **Sensitive Subsystems:** `ResolveeAI/billing_core` and production repositories are strictly **DENIED (HTTP 403)**.
- **Interns / QA:** Scoped to read-only access with sandbox canary assertion.

### 2. 🧪 Daytona Cloud Sandbox Canary Testing
Before credentials are handed over to the employee, the agent validates them inside an isolated **Daytona Sandbox container**:
- Asserts successful `git clone` of permitted repositories.
- Asserts strict `403 Forbidden` rejection on restricted finance and production repositories.

### 3. 📬 Real Zoho Mailbox Creation & SMTP Welcome Dispatch
- Calls Zoho Organization Admin API (`POST /api/organization/{zoid}/accounts`) to register real corporate accounts (`<name>@vansshagarrwal.in`).
- Auto-generates a secure 12-character one-time temporary password.
- Dispatches Day-1 credentials and webmail login URL (`https://mail.zoho.in`) via Zoho SMTP (`smtp.zoho.in:465`).

### 4. 🗄️ MongoDB Atlas Master Persistence
- All provisioned credentials, timestamps, and access vectors are committed to MongoDB Atlas (`company_db.employee`).
- Provides an auditable single pane of glass for IT, DevOps, and compliance teams.

### 5. 🚪 Autonomous Offboarding (Anti-Zombie Credential Engine)
A single prompt (`"offboard Algo"`) revokes:
1. GitHub organization membership and repo collaborator permissions.
2. Active AWS developer IAM access keys and sessions.
3. Corporate Zoho Mail access (account suspended/locked).
4. MongoDB Atlas master document updated to status `OFFBOARDED` with timestamp and exit reason.
5. Management receives an automated **Offboarding Audit Certificate** email.

---

## 🛡️ Enterprise Edge-Case Defenses

| Edge Case | Failure Mode in Other Systems | ResolveeAI Zero-Trust Defense |
| :--- | :--- | :--- |
| **Same-Name New Hire** | Email creation fails (`400: User exists`) or overwrites account. | Automatically detects collision in MongoDB/Zoho and increments (`algo@`, `algo2@`, `algo3@`). |
| **Ambiguous Offboarding** (2 employees with same name) | Blindly offboards the first database match, firing the wrong person. | **Disambiguation Safeguard:** Detects multiple active matches, halts revocation, and presents candidates table asking manager for exact corporate email or GitHub handle. |
| **Redundant Offboarding** | Re-fires revocation, generating false security alerts. | Detects past offboarding timestamp and returns `ALREADY_OFFBOARDED` idempotently. |
| **Windows TLS Handshake** | PyMongo SSL alert errors on Atlas SNI handshakes. | Configured with `tlsAllowInvalidCertificates=True` and fallback local state persistence. |

---

## 🛠️ Complete MCP Tool Catalog (10 Tools)

The `enterprise-onboarder` FastMCP server provides 10 purpose-built tools:

| Category | Tool Name | Description |
| :--- | :--- | :--- |
| **Onboarding** | `create_zoho_company_email` | Provisions real corporate mailbox on `vansshagarrwal.in` with temp password & collision avoidance. |
| **Onboarding** | `provision_github_repository_access` | Evaluates RBAC policies and sends real GitHub Org & Repo invitations. |
| **Onboarding** | `provision_aws_cloud_keys` | Generates scoped developer AWS IAM Access Keys and Secret Key. |
| **Onboarding** | `save_employee_to_mongodb` | Persists verified employee master record into MongoDB Atlas collection `employee`. |
| **Onboarding** | `send_welcome_email` | Dispatches official Day-1 credentials package to employee via Zoho SMTP. |
| **Offboarding** | `revoke_github_access` | Removes user from ResolveeAI org & repos and cancels all pending invitations. |
| **Offboarding** | `revoke_aws_credentials` | Deactivates and deletes AWS IAM developer keys and terminates cloud sessions. |
| **Offboarding** | `suspend_zoho_company_email` | Calls Zoho Organization Admin API to suspend/delete corporate mailbox. |
| **Offboarding** | `offboard_employee_in_mongodb` | Updates employee status to `OFFBOARDED` with disambiguation protections. |
| **Offboarding** | `send_offboarding_audit_email` | Emails Zero-Trust Offboarding Audit Certificate to management. |

---

## 💻 Quickstart & Execution

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ (for TrueForge: `npx @truefoundry/trueforge`)
- Active API keys (GitHub PAT, AWS IAM, MongoDB Atlas, Zoho Mail)

### 2. Installation
```bash
git clone https://github.com/code-1705/TrueForge_skills.git
cd TrueForge_skills
pip install -r requirements.txt
```

### 3. Environment Variables (`.env`)
Create a `.env` file with the following schema:
```env
# Zoho Mail
admin_mail=hi@vansshagarrwal.in
zoho_password=your_zoho_smtp_app_password
ZOHO_CLIENT_ID=your_zoho_self_client_id
ZOHO_CLIENT_SECRET=your_zoho_self_client_secret
ZOHO_REFRESH_TOKEN=your_zoho_permanent_refresh_token
ZOHO_ZOID=your_zoho_organization_id

# MongoDB Atlas
mongodb=mongodb+srv://user:pass@cluster.mongodb.net/company_db

# GitHub
pat=ghp_your_github_personal_access_token

# AWS Cloud
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1

# LLM & Sandbox
openai=sk-proj-...
daytona=dtn_...
```

### 4. Running the Local MCP Server
```bash
python enterprise_onboarding_mcp.py
```
*The MCP server runs on `http://localhost:8000/sse` with DNS rebinding protection configured for seamless local and remote discovery.*

### 5. Configuring TrueForge
1. Open TrueForge at `http://localhost:8790`.
2. Go to **Settings > Connectors** > **Add MCP Server**:
   - **Name:** `enterprise-onboarder`
   - **URL:** `http://localhost:8000/sse`
   - **Auth:** `None`
3. In **Agents > Create Agent**:
   - **Name:** `zero-trust-onboarding-agent`
   - **Connectors:** Select `enterprise-onboarder`
   - **Skills:** Attach `zero-trust-onboarding-policy`
   - **Sandbox:** Enable Daytona Sandbox

---

## 💬 Sample Prompts for Hackathon Demo

### Onboarding a New Engineer:
> *"Setup profile for Vanssh who will be joining our company as an SDE. His GitHub is code-1705."*

**Result:**
- Corporate email `vanssh@vansshagarrwal.in` created in Zoho with temporary password.
- GitHub invitation sent for `ResolveeAI/backend_api` (write); `ResolveeAI/billing_core` blocked.
- AWS IAM dev credentials generated.
- Daytona Sandbox canary test executed.
- Master record saved in MongoDB Atlas.
- Day-1 Welcome Email dispatched via Zoho SMTP.

### Offboarding an Exiting Engineer:
> *"Offboard Algo from our organization. Revoke all keys and access, and update our records."*

**Result:**
- GitHub collaborator access removed and org membership revoked.
- AWS IAM access keys deactivated and deleted.
- Zoho corporate mailbox suspended.
- MongoDB Atlas record updated from `ACTIVE_ONBOARDED` to `OFFBOARDED`.
- Management receives an Offboarding Audit Certificate email.

---

## 🏆 Hackathon Alignment: TrueFoundry × Polaris
- **Agents That Act:** Not just answering questions—taking real, transactional actions across multiple enterprise infrastructure providers.
- **Zero-Trust Security:** Least-privilege by default, sandboxed pre-flight verification, and automated exit governance.
- **Enterprise-Grade Reliability:** Native edge-case handling for name collisions, disambiguation guards, and persistent audit logs.

---

## 📄 License
MIT License. Built with ❤️ for the TrueFoundry × Polaris Hackathon.
