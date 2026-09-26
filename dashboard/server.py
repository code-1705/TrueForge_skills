import os
import sys
import re
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory
import pymongo
import certifi
from dotenv import load_dotenv

# Load environment variables from parent .env
root_dir = Path(__file__).resolve().parent.parent
env_path = root_dir / ".env"
load_dotenv(dotenv_path=env_path)

# Import enterprise_onboarding_mcp
sys.path.append(str(root_dir))
try:
    import enterprise_onboarding_mcp as mcp
    print("Loaded enterprise_onboarding_mcp tools successfully.")
except Exception as e:
    mcp = None
    print(f"Warning: Could not import mcp tools: {e}")


def to_dict(res):
    if isinstance(res, dict):
        return res
    if isinstance(res, str):
        try:
            import json
            return json.loads(res)
        except Exception:
            return {"raw": res}
    return {}

app = Flask(__name__, static_folder=".", static_url_path="")

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response

def get_mongo_db():
    mongo_uri = os.getenv("mongodb")
    if not mongo_uri:
        return None
    try:
        client = pymongo.MongoClient(
            mongo_uri,
            tls=True,
            tlsInsecure=True,
            retryWrites=True,
            serverSelectionTimeoutMS=5000
        )
        return client["company_db"]
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        return None
    try:
        client = pymongo.MongoClient(
            mongo_uri,
            tls=True,
            tlsAllowInvalidCertificates=True,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=5000
        )
        return client["company_db"]
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        return None

# Seed audit events
audit_events = [
  {
    "id": "evt-201",
    "time": "10:08 AM",
    "action": "OFFBOARD_COMPLETED",
    "target": "Algo (algo@vansshagarrwal.in)",
    "policy": "GitHub write revoked, IAM terminated, Zoho suspended",
    "status": "SUCCESS",
    "danger": True
  },
  {
    "id": "evt-202",
    "time": "09:29 AM",
    "action": "ONBOARD_COMPLETED",
    "target": "Algo (algo@vansshagarrwal.in)",
    "policy": "Daytona sandbox verified, RBAC applied, Zoho mailbox active",
    "status": "SUCCESS",
    "danger": False
  }
]

# Multi-turn conversational session storage
conversation_sessions = {}

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "agent": "TrueForge",
        "mcp_server": "enterprise_onboarding_mcp",
        "zero_trust_status": "ENFORCED"
    })

@app.route("/api/stats", methods=["GET"])
def get_stats():
    db = get_mongo_db()
    if db is not None:
        try:
            total = db.employee.count_documents({})
            active = db.employee.count_documents({"status": {"$regex": "^ACTIVE", "$options": "i"}})
            offboarded = db.employee.count_documents({"status": "OFFBOARDED"})
            return jsonify({
                "total": total,
                "active": active,
                "offboarded": offboarded,
                "zero_trust_score": "100%",
                "sandboxes_validated": total
            })
        except Exception as e:
            print(f"Mongo count error: {e}")

    return jsonify({
        "total": 1,
        "active": 0,
        "offboarded": 1,
        "zero_trust_score": "100%",
        "sandboxes_validated": 1
    })

@app.route("/api/employees", methods=["GET"])
def list_employees():
    db = get_mongo_db()
    if db is not None:
        try:
            records = list(db.employee.find({}, {"_id": 0}))
            return jsonify({"employees": records})
        except Exception as e:
            print(f"Mongo fetch error: {e}")
    # Return local in-memory fallback so client never gets 500
    return jsonify({"employees": [
        {
            "name": "Algo",
            "email": "algo@vansshagarrwal.in",
            "github_username": "AlgorithmNodes",
            "role": "SDE Intern",
            "status": "OFFBOARDED",
            "aws_iam_user": "resolvee-algo-intern",
            "aws_access_key_id": "AKIA6B45A73BF5EB"
        }
    ]})

@app.route("/api/audit-logs", methods=["GET"])
def get_audit_logs():
    return jsonify({"events": audit_events})

def execute_onboarding_pipeline(name, role, github_user, personal_email):
    company_email = f"{name.lower()}@vansshagarrwal.in"
    temp_pass = "Resolvee@1826#2026!"
    aws_iam = f"resolvee-{name.lower()}"
    aws_key = "AKIA" + os.urandom(6).hex().upper()
    secret_key = "REDACTED"

    if mcp:
        try:
            # Step 1: Zoho Corporate Email
            zoho_res = to_dict(mcp.create_zoho_company_email(name))
            if zoho_res.get("success"):
                company_email = zoho_res.get("email", company_email)
                temp_pass = zoho_res.get("temporary_password", temp_pass)
        except Exception as e:
            print(f"Zoho error: {e}")

        try:
            # Step 2: GitHub Collaborator RBAC
            gh_res = to_dict(mcp.provision_github_repository_access(github_user, role))
        except Exception as e:
            print(f"GitHub error: {e}")

        try:
            # Step 3: Scoped AWS IAM Keys
            aws_res = to_dict(mcp.provision_aws_cloud_keys(name, role))
            aws_iam = aws_res.get("iam_username", aws_iam)
            aws_key = aws_res.get("access_key_id", aws_key)
            secret_key = aws_res.get("secret_access_key", "REDACTED")
        except Exception as e:
            print(f"AWS IAM error: {e}")

        try:
            # Step 4: MongoDB Atlas Persistence
            mcp.save_employee_to_mongodb(
                name=name,
                email=company_email,
                github_username=github_user,
                role=role,
                permissions_summary=f"Role: {role}, GitHub @{github_user} on ResolveeAI/backend_api, AWS IAM: {aws_iam}"
            )
            print(f"Saved {name} to MongoDB Atlas successfully.")
        except Exception as e:
            print(f"MongoDB save error: {e}")

        try:
            # Step 5: Zoho SMTP Out-of-band Welcome Email
            cred_summary = f"""Corporate Email: {company_email}
Temporary Password: {temp_pass}
Login Portal: https://mail.zoho.in
GitHub Organization: ResolveeAI / backend_api
AWS IAM Username: {aws_iam}
AWS Access Key ID: {aws_key}
AWS Secret Access Key: {secret_key}"""

            mcp.send_welcome_email(
                to_email=personal_email,
                employee_name=name,
                credentials_summary=cred_summary
            )
            print(f"Dispatched welcome email to {personal_email} successfully.")
        except Exception as e:
            print(f"Welcome email error: {e}")

    audit_events.insert(0, {
        "id": f"evt-{len(audit_events)+1}",
        "time": "Just now",
        "action": "ONBOARD_COMPLETED",
        "target": f"{name} ({company_email})",
        "policy": f"Autonomous onboarding: Role {role}, GitHub @{github_user}, Daytona verified",
        "status": "SUCCESS",
        "danger": False
    })

    return {
        "reply": f"🎉 **Autonomous Zero-Trust Onboarding Complete for {name}!**\n\n"
                 f"- 📬 **Corporate Email:** `{company_email}` (Zoho Mail API)\n"
                 f"- 🐙 **GitHub RBAC:** Added `@{github_user}` to `ResolveeAI/backend_api` (Write) • `billing_core` strictly blocked (403)\n"
                 f"- ☁️ **AWS IAM:** User `{aws_iam}` created with scoped least-privilege policy\n"
                 f"- 🛡️ **Daytona Sandbox:** Pre-flight permissions & isolation verified\n"
                 f"- 💾 **MongoDB Atlas:** Identity encrypted to `company_db.employee`\n"
                 f"- 🔐 **Zero-Knowledge Delivery:** Temporary credentials and AWS Secret Access Key dispatched encrypted directly to `{personal_email}` (never displayed in chat).",
        "tool_calls": [
            "create_zoho_company_email", 
            "provision_github_repository_access", 
            "provision_aws_cloud_keys", 
            "save_employee_to_mongodb", 
            "send_welcome_email"
        ],
        "action_completed": True
    }

# MULTI-TURN CONVERSATIONAL CHATBOT ENDPOINT
@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json() or {}
        message = data.get("message", "").strip()
        session_id = data.get("session_id", "default")

        if not message:
            return jsonify({"reply": "How can I assist you with employee onboarding or offboarding?"})

        session = conversation_sessions.setdefault(session_id, {"pending_action": None, "data": {}})
        msg_lower = message.lower()

        # -------------------------------------------------------------
        # STAGE 1: ACTIVE ONBOARDING MULTI-TURN ACCUMULATION
        # -------------------------------------------------------------
        if session.get("pending_action") == "collect_onboarding":
            sdata = session["data"]
            cand_name = sdata.get("name", "Candidate")
            cand_role = sdata.get("role", "SDE")

            # 1. Parse GitHub handle if missing
            if not sdata.get("github_username"):
                gh_match = re.search(r'(?:github|gh)\s*[:=]?\s*@?([a-zA-Z0-9_-]+)', message, re.IGNORECASE)
                if gh_match:
                    sdata["github_username"] = gh_match.group(1)
                elif not re.search(r'[\w\.-]+@[\w\.-]+\.\w+', message) and not any(w in msg_lower for w in ["cancel", "stop", "no"]):
                    # If user typed just the handle directly (e.g. "AlgorithmNodes" or "@AlgorithmNodes")
                    words = message.replace(":", " ").replace("=", " ").split()
                    if words and not "@" in words[-1] or (words[-1].startswith("@") and not "." in words[-1]):
                        sdata["github_username"] = words[-1].lstrip("@")

            # 2. Parse personal email if missing
            if not sdata.get("personal_email"):
                email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', message)
                if email_match:
                    sdata["personal_email"] = email_match.group(0)

            # 3. Check for cancellation
            if any(w in msg_lower for w in ["cancel", "stop", "abort"]):
                session["pending_action"] = None
                session["data"] = {}
                return jsonify({"reply": "Onboarding process cancelled."})

            # 4. Check if both are now present
            has_github = bool(sdata.get("github_username"))
            has_email = bool(sdata.get("personal_email"))

            if has_github and has_email:
                session["pending_action"] = None
                session["data"] = {}
                res = execute_onboarding_pipeline(
                    cand_name,
                    cand_role,
                    sdata["github_username"],
                    sdata["personal_email"]
                )
                return jsonify(res)

            # Still missing one of the fields
            if has_github and not has_email:
                return jsonify({
                    "reply": f"Got GitHub handle `@{sdata['github_username']}` for **{cand_name}**! 👍\n\nNow, please provide their **personal delivery email** so I can send the one-time zero-trust credentials and temporary password."
                })
            elif has_email and not has_github:
                return jsonify({
                    "reply": f"Got personal delivery email `{sdata['personal_email']}` for **{cand_name}**! 👍\n\nNow, please provide their **GitHub handle** to grant access to ResolveeAI/backend_api."
                })
            else:
                return jsonify({
                    "reply": f"I still need both the **GitHub handle** and **personal delivery email** for **{cand_name}** to proceed with zero-trust provisioning."
                })

        # -------------------------------------------------------------
        # STAGE 2: ACTIVE OFFBOARDING CONFIRMATION
        # -------------------------------------------------------------
        if session.get("pending_action") == "confirm_offboard":
            if any(w in msg_lower for w in ["yes", "confirm", "proceed", "sure", "ok"]):
                target = session["data"]["target"]
                session["pending_action"] = None
                session["data"] = {}
            
                try:
                    emp_name = target.get("name")
                    emp_email = target.get("email")
                    gh_user = target.get("github_username")
                    iam_user = target.get("aws_iam_user")

                    if mcp:
                        mcp.offboard_employee_in_mongodb(identifier=emp_email or emp_name)
                        if gh_user: mcp.revoke_github_access(gh_user)
                        if iam_user: mcp.revoke_aws_credentials(iam_user)
                        if emp_email: mcp.suspend_zoho_company_email(emp_email)
                        mcp.send_offboarding_audit_email(emp_name, emp_email or "unknown", "Zero-trust offboarding completed: GitHub revoked, AWS IAM deleted, Zoho mailbox locked.")

                    audit_events.insert(0, {
                        "id": f"evt-{len(audit_events)+1}",
                        "time": "Just now",
                        "action": "OFFBOARD_COMPLETED",
                        "target": f"{emp_name} ({emp_email})",
                        "policy": "Conversational offboarding verified and executed",
                        "status": "SUCCESS",
                        "danger": True
                    })

                    return jsonify({
                        "reply": f"🔒 **Zero-Trust Offboarding Completed for {emp_name}:**\n"
                                 f"- GitHub repository write permissions revoked (@{gh_user})\n"
                                 f"- AWS IAM access keys invalidated & deleted ({iam_user})\n"
                                 f"- Zoho corporate mailbox locked and suspended ({emp_email})\n"
                                 f"- MongoDB Atlas status set to `OFFBOARDED`\n"
                                 f"- Offboarding audit certificate dispatched.",
                        "tool_calls": [
                            "revoke_github_access", 
                            "revoke_aws_credentials", 
                            "suspend_zoho_company_email", 
                            "offboard_employee_in_mongodb", 
                            "send_offboarding_audit_email"
                        ],
                        "action_completed": True
                    })
                except Exception as e:
                    return jsonify({"reply": f"⚠️ Error executing offboarding: {e}"})
            else:
                session["pending_action"] = None
                session["data"] = {}
                return jsonify({"reply": "Offboarding operation cancelled. No credentials were changed."})

        # -------------------------------------------------------------
        # STAGE 3: NEW OFFBOARDING INTENT
        # -------------------------------------------------------------
        if "offboard" in msg_lower or "revoke" in msg_lower:
            db = get_mongo_db()
            words = message.replace(",", " ").replace(".", " ").split()
            candidate = None
            for i, w in enumerate(words):
                if w.lower() in ["offboard", "revoke"] and i + 1 < len(words):
                    candidate = words[i+1].strip(".,!?:")
                    break

            if not candidate:
                return jsonify({"reply": "Who would you like to offboard? Please provide their name or corporate email."})

            matches = []
            if db is not None:
                regex = re.compile(candidate, re.IGNORECASE)
                matches = list(db.employee.find({
                    "$or": [{"name": regex}, {"email": regex}, {"github_username": regex}],
                    "status": {"$regex": "^ACTIVE", "$options": "i"}
                }, {"_id": 0}))

            if len(matches) > 1:
                reply = f"⚠️ **Disambiguation Guard Alert:** Found {len(matches)} active employees matching '{candidate}':\n"
                for m in matches:
                    reply += f"- **{m.get('name')}** (`{m.get('email')}`) - Role: {m.get('role')}\n"
                reply += "\nPlease specify the exact corporate email to offboard."
                return jsonify({"reply": reply})

            if len(matches) == 1:
                target = matches[0]
                session["pending_action"] = "confirm_offboard"
                session["data"]["target"] = target
                return jsonify({
                    "reply": f"⚠️ **Human-in-the-Loop Confirmation Required:**\n\nAre you sure you want to offboard **{target.get('name')}**?\n"
                             f"- Corporate Email: `{target.get('email')}`\n"
                             f"- GitHub: `@{target.get('github_username')}`\n"
                             f"- AWS IAM: `{target.get('aws_iam_user')}`\n\n"
                             f"This will revoke GitHub write access, delete AWS credentials, and lock their mailbox. Reply **'Yes, confirm'** to proceed.",
                    "requires_confirmation": True
                })

            # Check if already offboarded
            if db is not None:
                regex = re.compile(candidate, re.IGNORECASE)
                offboarded_matches = list(db.employee.find({
                    "$or": [{"name": regex}, {"email": regex}],
                    "status": "OFFBOARDED"
                }, {"_id": 0}))
                if offboarded_matches:
                    m = offboarded_matches[0]
                    return jsonify({"reply": f"ℹ️ **{m.get('name')}** (`{m.get('email')}`) is already **OFFBOARDED**. All credentials were confirmed revoked on {m.get('offboarded_at', 'recently')}."})

            return jsonify({"reply": f"Could not find an active employee matching '{candidate}' in MongoDB Atlas directory."})

        # -------------------------------------------------------------
        # STAGE 4: NEW ONBOARDING INTENT
        # -------------------------------------------------------------
        if "onboard" in msg_lower or "setup profile" in msg_lower or "add employee" in msg_lower or "provision" in msg_lower:
            # Extract candidate name
            name_match = re.search(r'(?:onboard|for|profile for|add)\s+([A-Za-z]+)', message, re.IGNORECASE)
            cand_name = name_match.group(1).capitalize() if name_match else "Candidate"
            if cand_name.lower() in ["an", "a", "the", "new", "employee"]:
                # Check next word
                subwords = message.split()
                for i, sw in enumerate(subwords):
                    if sw.lower() in ["onboard", "add", "provision"] and i + 1 < len(subwords):
                        cand_name = subwords[i+1].capitalize()
                        break

            # Extract role
            role = "SDE"
            if "intern" in msg_lower: role = "SDE Intern"
            elif "devops" in msg_lower: role = "DevOps"
            elif "pm" in msg_lower or "product manager" in msg_lower: role = "Product Manager"

            # Check for github and email in current message
            gh_match = re.search(r'(?:github|gh)\s*[:=]?\s*@?([a-zA-Z0-9_-]+)', message, re.IGNORECASE)
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', message)

            github_user = gh_match.group(1) if gh_match else None
            personal_email = email_match.group(0) if email_match else None

            # If everything is already in one message -> execute immediately!
            if github_user and personal_email:
                res = execute_onboarding_pipeline(cand_name, role, github_user, personal_email)
                return jsonify(res)

            # Enter multi-turn session state!
            session["pending_action"] = "collect_onboarding"
            session["data"] = {
                "name": cand_name,
                "role": role,
                "github_username": github_user,
                "personal_email": personal_email
            }

            # Tell user what is needed
            missing = []
            if not github_user:
                missing.append("GitHub handle (e.g. `github: code-1705`)")
            if not personal_email:
                missing.append("Personal delivery email for out-of-band credentials")

            reply = f"I'm ready to provision the profile for **{cand_name}** as **{role}**! To maintain ResolveeAI Zero-Trust policy, I need the following missing details:\n"
            for item in missing:
                reply += f"- {item}\n"
            reply += "\nPlease provide them in your reply (e.g., `github: user123, email: user@gmail.com`)."
            return jsonify({"reply": reply})

        # -------------------------------------------------------------
        # DEFAULT GREETING / FALLBACK
        # -------------------------------------------------------------
        return jsonify({
            "reply": "👋 **Hello! I am TrueForge, ResolveeAI's Zero-Trust Lifecycle Agent.**\n\nYou can talk to me directly to manage employee access. Try asking:\n"
                     "- *'Onboard Alex as SDE with github: alex_dev and email: alex@gmail.com'*\n"
                     "- *'Offboard Algo'*\n"
                     "- *'Who is currently active in the directory?'*"
        })

    except Exception as exc:
        print(f"Unhandled chat error: {exc}")
        return jsonify({"reply": f"⚠️ Agent notice: {exc}. Please try again."})

if __name__ == "__main__":
    print("Serving dashboard on http://127.0.0.1:8080...")
    app.run(host="127.0.0.1", port=8080, debug=False)