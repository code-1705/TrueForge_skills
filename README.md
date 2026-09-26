# ResolveeAI: Autonomous Zero-Trust Lifecycle Agent

> **Agents That Act: TrueFoundry × Polaris Hackathon** | Autonomous IT & Security Officer powered by TrueForge.

---

### 1. The Problem
Enterprise employee lifecycle management suffers from slow, ticket-heavy onboarding (3–5 days) and dangerous "zombie credentials" during offboarding (over 80% of former employees retain unauthorized access), causing widespread security and compliance violations.

---

### 2. What the Agent Reaches
Via a dedicated FastMCP server (`enterprise_onboarding_mcp.py`), the agent autonomously connects to:
- **Zoho Directory API:** Provisions corporate inboxes (`@vansshagarrwal.in`) and suspends mailboxes.
- **GitHub REST API:** Manages collaborator and org permissions on `ResolveeAI`.
- **AWS IAM Engine:** Generates and invalidates scoped developer credentials.
- **Daytona Sandboxes:** Validates developer permissions inside isolated canary environments.
- **MongoDB Atlas (`company_db.employee`):** Persists and audits identity lifecycle records.
- **Zoho SMTP:** Delivers out-of-band welcome credentials and tamper-evident audit certificates.

---

### 3. Where It Stops (Guardrails & Boundaries)
- **Zero-Trust Policy:** Strictly denies access to sensitive repositories (`ResolveeAI/billing_core` returns HTTP 403).
- **Human-in-the-Loop (HITL) Gate:** Requires explicit managerial confirmation before irreversible offboarding.
- **Disambiguation Guard:** Halts execution if multiple active employees share identical names.
- **Zero-Knowledge Secret Masking:** AWS Secret Access Keys are never exposed in chats or dashboards—dispatched encrypted out-of-band directly to private inboxes.

---

### 4. Architecture & How TrueForge Was Used
```
[ Hosted UI / Chat ] ──► [ TrueForge Autonomous Agent ] ──► [ FastMCP Server ] ──► [ Enterprise Perimeter ]
                                 │                                                 (Zoho, GitHub, AWS,
                                 ▼                                                  Daytona, MongoDB)
                      Policy: SKILL.md + Guardrails
```
**TrueForge** operates as the core reasoning engine. It executes multi-turn parameter discovery, interprets zero-trust rules from `skills/onboarding-policy/SKILL.md`, enforces disambiguation guards, and orchestrates live MCP tool calls.

---

### 5. What Is Real vs. Mocked
- **Real:** Live Zoho Admin OAuth2 inboxes, real GitHub collaborator invitations and org membership, live MongoDB Atlas cluster persistence, real AWS IAM developer keys, and real Zoho TLS email delivery.
- **Mocked / Simulated:** `billing_core` 403 enforcement (simulated policy trap) and Daytona sandbox pre-flight verification probe (tested via API payload simulation when token is in test mode).

---

### 6. Known Limits
- Domain restricted to `@vansshagarrwal.in`.
- GitHub members must accept the emailed invitation link before appearing as public organization members.
- Windows PyMongo requires `tlsInsecure=True` to bypass local OpenSSL SRV shard handshake alerts.

---

### 7. ⚡ Quickstart & Setup
```bash
# 1. Clone repository
git clone https://github.com/code-1705/TrueForge_skills.git && cd TrueForge_skills

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env  # fill in Zoho, GitHub, AWS, Mongo, Daytona keys

# 4. Start FastMCP Enterprise Server
python enterprise_onboarding_mcp.py

# 5. Launch TrueForge Autonomous Agent
npx trueforge
```
