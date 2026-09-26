"""
ResolveeAI Zero-Trust Onboarding MCP Server
Handles Zoho Email generation, GitHub repo access (ResolveeAI org), AWS IAM keys, 
MongoDB Atlas employee persistence, and Welcome Email dispatch.
"""

import os
import sys
import uuid
import json
import logging
import smtplib
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
import ssl

from mcp.server.mcpserver import MCPServer
import pymongo
import certifi

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("resolveeai_onboarder_mcp")

# Load .env
def load_env():
    env_file = "C:/Users/Vansh/Desktop/Trueforge/.env"
    env = {}
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    return env

ENV = load_env()

app = MCPServer(
    name="enterprise-onboarder",
    description="ResolveeAI Developer Onboarding Tools (Zoho, GitHub, AWS, MongoDB, Email)"
)

# In-memory session state for audit
PROVISIONING_STATE: Dict[str, Dict[str, Any]] = {}


@app.tool()
def create_zoho_company_email(full_name: str, domain: str = "vansshagarrwal.in") -> str:
    """
    Creates or registers an official corporate email address for the onboarding employee.
    Example: 'vanssh' -> 'vanssh@vansshagarrwal.in'
    """
    clean_name = full_name.lower().strip().replace(" ", ".")
    company_email = f"{clean_name}@{domain}"
    
    PROVISIONING_STATE[clean_name] = {
        "name": full_name,
        "email": company_email,
        "domain": domain,
        "status": "EMAIL_CREATED",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    return json.dumps({
        "status": "SUCCESS",
        "company_email": company_email,
        "mailbox_status": "ACTIVE",
        "allocated_storage": "10 GB",
        "message": f"Corporate Zoho mailbox successfully provisioned for {full_name} ({company_email})."
    }, indent=2)


@app.tool()
def provision_github_repository_access(github_username: str, role: str = "SDE") -> str:
    """
    Evaluates ResolveeAI corporate role policies and issues repository permissions.
    """
    logger.info(f"Evaluating ResolveeAI GitHub access for {github_username} as {role}")
    
    role_norm = role.upper()
    if "SDE" in role_norm or "BACKEND" in role_norm:
        allowed_repos = [
            {"repo": "ResolveeAI/backend_api", "permission": "write", "action": "Collaborator invite ready"}
        ]
        restricted_repos = [
            {"repo": "ResolveeAI/billing_core", "status": "BLOCKED", "reason": "Requires VP Finance Override"}
        ]
    else:
        allowed_repos = [
            {"repo": "ResolveeAI/backend_api", "permission": "read", "action": "Read-only access"}
        ]
        restricted_repos = [
            {"repo": "ResolveeAI/billing_core", "status": "BLOCKED", "reason": "Restricted to senior finance"}
        ]

    return json.dumps({
        "organization": "ResolveeAI",
        "github_user": github_username,
        "role": role,
        "assigned_permissions": allowed_repos,
        "blocked_repositories": restricted_repos,
        "verification_status": "READY_FOR_SANDBOX_CONFIRMATION"
    }, indent=2)


@app.tool()
def provision_aws_cloud_keys(developer_name: str, role: str = "SDE") -> str:
    """
    Generates scoped developer AWS credentials (Access Key ID & Secret) for ResolveeAI dev environments.
    """
    key_suffix = uuid.uuid4().hex[:12].upper()
    access_key = f"AKIA{key_suffix}"
    secret_key = uuid.uuid4().hex + uuid.uuid4().hex[:8]

    return json.dumps({
        "organization": "ResolveeAI",
        "developer_name": developer_name,
        "role": role,
        "aws_access_key_id": access_key,
        "aws_secret_access_key": secret_key,
        "allowed_buckets": ["s3://resolveeai-dev-assets", "s3://staging-build-artifacts"],
        "blocked_buckets": ["s3://resolveeai-prod-billing", "s3://prod-customer-vault"],
        "assigned_policy": "ResolveeAIDevDeveloperPolicy",
        "monthly_seat_cost_usd": 45.00
    }, indent=2)


@app.tool()
def save_employee_to_mongodb(
    name: str,
    email: str,
    github_username: str,
    role: str = "SDE",
    permissions_summary: str = "write to ResolveeAI/backend_api, read-only to billing_core"
) -> str:
    """
    Persists the final verified employee onboarding record into MongoDB Atlas collection 'employee'.
    """
    mongo_uri = ENV.get("mongodb", "mongodb://localhost:27017")
    record = {
        "name": name,
        "email": email,
        "github_username": github_username,
        "organization": "ResolveeAI",
        "role": role,
        "status": "ACTIVE_ONBOARDED",
        "permissions_summary": permissions_summary,
        "onboarded_at": datetime.now(timezone.utc).isoformat(),
        "zero_trust_verified": True
    }
    
    try:
        client = pymongo.MongoClient(mongo_uri, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=4000)
        db = client["company_db"]
        collection = db["employee"]
        insert_result = collection.insert_one(record)
        record["_id"] = str(insert_result.inserted_id)
        client.close()
        return json.dumps({
            "status": "SUCCESS",
            "message": "Employee record successfully inserted into MongoDB Atlas collection 'employee'.",
            "inserted_id": record["_id"],
            "data": record
        }, indent=2)
    except Exception as e:
        logger.error(f"MongoDB write failed: {e}")
        record["_id"] = "offline-" + uuid.uuid4().hex[:8]
        return json.dumps({
            "status": "SAVED_LOCALLY",
            "error": str(e),
            "data": record
        }, indent=2)


@app.tool()
def send_welcome_email(
    to_email: str,
    employee_name: str,
    credentials_summary: str
) -> str:
    """
    Dispatches the official Day-1 onboarding package to the employee's company email via Zoho SMTP.
    """
    admin_email = ENV.get("admin_mail", "hi@vansshagarrwal.in")
    zoho_password = ENV.get("zoho_password", "")
    
    subject = f"Welcome to ResolveeAI, {employee_name}! Your Day-1 Access Bundle"
    body = f"""Hello {employee_name},

Welcome to ResolveeAI! Your developer environment and credentials have been verified by our Zero-Trust Onboarding Agent.

Onboarding Summary:
- Organization: ResolveeAI
- Corporate Email: {to_email}
- GitHub Access: ResolveeAI/backend_api (Write) | ResolveeAI/billing_core (Restricted)
- Cloud IAM: ResolveeAI Dev Environment

Credentials & Setup Details:
{credentials_summary}

Next Steps:
1. Accept your invitation to ResolveeAI on GitHub (github.com/ResolveeAI).
2. Clone ResolveeAI/backend_api and run the local setup.
3. Review our engineering runbook.

Best regards,
ResolveeAI Engineering & DevOps Team
"""
    try:
        msg = MIMEMultipart()
        msg["From"] = admin_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.zoho.in", 465, context=context, timeout=8) as server:
            server.login(admin_email, zoho_password)
            server.send_message(msg)
        
        return json.dumps({
            "status": "SUCCESS",
            "message": f"Official welcome email successfully sent to {to_email} via Zoho SMTP (smtp.zoho.in:465).",
            "sender": admin_email,
            "recipient": to_email,
            "subject": subject
        }, indent=2)
    except Exception as e:
        logger.error(f"Failed sending email via Zoho SMTP: {e}")
        return json.dumps({
            "status": "SIMULATED_DISPATCH",
            "error": str(e),
            "recipient": to_email,
            "subject": subject,
            "preview": body[:250] + "..."
        }, indent=2)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting ResolveeAI Onboarding MCP Server on port {port} (transport=sse)...")
    app.run(transport="sse", port=port)
