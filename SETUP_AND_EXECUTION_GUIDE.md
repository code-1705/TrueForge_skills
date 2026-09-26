# Zero-Trust Developer Onboarding: Complete Setup & Execution Guide

This guide lists **every API key and credential** required for the project, explains how to set them up, answers the GitHub Organization question, and details how to execute the end-to-end flow.

---

## 1. Do You Need to Create a GitHub Organization?

### **Yes, highly recommended (Takes 60 seconds and is 100% Free).**

Why you should create an organization instead of using your personal profile:
1. **Enterprise Realism:** In a real company, repos are hosted under an organization (e.g., `github.com/my-tech-corp/backend-api`), not under a personal profile (`github.com/vansh/...`).
2. **Team & Role Governance:** GitHub Organizations support team roles (`Developers`, `Admins`) and granular repository permissions (`read`, `write`, `triage`).
3. **Clean Demo Environment:** You can create 2 dummy repos in the organization:
   - `backend-api` (Allowed repo for SDE)
   - `billing-core` (Restricted repo for SDE)
4. **How to create one:**
   - Go to [github.com/organizations/plan](https://github.com/organizations/plan)
   - Select the **Free** plan.
   - Name it (e.g., `acme-dev-corp` or `trueforge-enterprise`).
   - Your personal account is the Owner/Admin.

---

## 2. Master Checklist of All API Keys & Credentials

| # | Service | What It's Used For | Where to Get It | Where to Configure It |
|---|---|---|---|---|
| **1** | **LLM API Key** (OpenAI / Anthropic / Gemini) | Powers the TrueForge reasoning loop | [platform.openai.com](https://platform.openai.com) / [console.anthropic.com](https://console.anthropic.com) / [aistudio.google.com](https://aistudio.google.com) | TrueForge UI → **Settings → Models** |
| **2** | **Daytona API Key** | Isolated Linux Sandbox to run verification canary tests | [app.daytona.io](https://app.daytona.io) | TrueForge UI → **Settings → Sandbox providers** |
| **3** | **GitHub PAT (Classic)** | Provision repo invitations and check permissions | [github.com/settings/tokens](https://github.com/settings/tokens) | TrueForge UI → **Settings → Connectors → GitHub** |
| **4** | **Zoho Mail (SMTP / API)** | Sends the Day-1 onboarding email from official email | [zoho.com/mail](https://www.zoho.com/mail) | `.env` file (`ZOHO_EMAIL`, `ZOHO_PASSWORD`) |
| **5** | **MongoDB Connection URI** | Stores employee records in the `employee` collection | Local MongoDB (`mongodb://localhost:27017`) or [cloud.mongodb.com](https://cloud.mongodb.com) | `.env` file (`MONGODB_URI`) |
| **6** | **AWS IAM Keys** *(Optional)* | Generates scoped developer IAM credentials | AWS Console → IAM → Users → Security Credentials | `.env` file (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`) |

---

## 3. How to Set Up Each Credential

### A. Daytona API Key (Sandbox)
1. Sign in to [app.daytona.io](https://app.daytona.io).
2. Go to **API Keys** → **Create API Key**.
3. **Important:** Select permissions:
   - **Sandboxes:** Read & Write
   - **Snapshots:** Write / Create
4. Copy the key → In TrueForge: **Settings → Sandbox providers → Daytona → Configure** → Paste and Save.

### B. GitHub PAT (Classic)
1. Go to [github.com/settings/tokens](https://github.com/settings/tokens).
2. Click **Generate new token (classic)**.
3. Check scopes:
   - `repo` (Full control)
   - `admin:org` (Full control to invite members to the org)
   - `user` (`read:user`, `user:email`)
4. Copy token → In TrueForge: **Settings → Connectors → GitHub** → Paste and Save.

### C. Zoho Mail (App Password)
1. Log in to your Zoho Mail account ([zoho.com/mail](https://www.zoho.com/mail)).
2. Go to **My Account** (`accounts.zoho.com`) → **Security** → **App Passwords**.
3. Click **Generate New Password** → Name it `TrueForge-Onboarding`.
4. Copy the 16-character password.
   - SMTP Server: `smtp.zoho.com` (or `smtp.zoho.in` if in India)
   - Port: `465` (SSL) or `587` (TLS)

### D. MongoDB
* **Option 1 (Local):** Run local MongoDB on `mongodb://localhost:27017`.
* **Option 2 (Cloud Atlas):** Create a free cluster on [cloud.mongodb.com](https://cloud.mongodb.com) and copy your connection string:
  `mongodb+srv://<user>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority`

### E. AWS (IAM Credentials)
* If you have an AWS account with IAM permissions, create an IAM user with `IAMFullAccess` (or Administrator) for the provisioner:
  - `AWS_ACCESS_KEY_ID=AKIA...`
  - `AWS_SECRET_ACCESS_KEY=...`
  - `AWS_REGION=us-east-1`
* *(If omitted, our Python server automatically generates valid mock keys so testing never fails).*

---

## 4. Environment File (`.env`)

Create a `.env` file in `C:\Users\Vansh\Desktop\Trueforge\.env`:

```env
# Zoho Mail Configuration
ZOHO_SMTP_HOST=smtp.zoho.in
ZOHO_SMTP_PORT=465
ZOHO_OFFICIAL_EMAIL=admin@yourdomain.com
ZOHO_APP_PASSWORD=your_16_char_app_password

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=company_db
MONGODB_COLLECTION=employee

# AWS Configuration (Optional - falls back to safe simulation if empty)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1

# Server Port
PORT=8000
```

---

## 5. How to Run and Execute the System

### Step 1: Start the Custom Onboarding MCP Server
In your terminal, navigate to `C:\Users\Vansh\Desktop\Trueforge` and run:
```bash
python enterprise_onboarding_mcp.py
```
*Output will confirm:*
```
INFO: Uvicorn running on http://127.0.0.1:8000 (transport=sse)
```

### Step 2: Connect the Server in TrueForge
1. Open **[http://localhost:8790](http://localhost:8790)**.
2. Go to **Settings → Connectors**.
3. Click **Add MCP Server**:
   - **Name:** `enterprise-onboarder`
   - **URL:** `http://localhost:8000/sse`
   - **Auth:** `No auth`
4. Click **Save & Connect**.

### Step 3: Configure the Agent in TrueForge
1. Click **Build Agent**.
2. **Name:** `zero-trust-onboarder`
3. **Model:** Select `claude-3-5-sonnet` or `gpt-4o`.
4. **Skills:** Enable `zero-trust-onboarding-policy`.
5. **Connectors:** Attach both `github` and `enterprise-onboarder`.
6. **Tool Approvals:** Toggle the shield on for `provision_aws_keys`, `save_employee_to_mongodb`, and `send_welcome_email`.
7. **Runtime Config:** Ensure **Sandbox** is **ON**.
8. Click **Save Agent**.

---

## 6. The Execution Prompt (Try it in Chat!)

Go to **Agents** → select `zero-trust-onboarder` → click **New Chat**, then send:

> **"setup profile for vanssh who will be joining our company as SDE. his github : code-1705"**

### What Happens:
1. **Identity Step:** Agent calls `create_zoho_company_email` → creates `vanssh@company.com`.
2. **Policy Step:** Agent reads `SKILL.md` → determines SDE permissions (`backend-api` write, `billing-core` blocked).
3. **Provisioning Step:** Agent generates repository invites and AWS dev IAM keys.
4. **Verification Step (Daytona):** Agent boots the sandbox and runs real tests (confirms git access, confirms 403 on billing).
5. **Human Gate:** TrueForge pauses and displays **Allow / Deny** for the manager.
6. **Database Step:** Once allowed, writes the profile into MongoDB collection `employee`.
7. **Delivery Step:** Sends the welcome email to `vanssh@company.com` from `admin@yourdomain.com`.
