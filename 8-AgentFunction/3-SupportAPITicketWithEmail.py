import os
import json
import uuid
import re
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import AzureOpenAI
from fastapi.middleware.cors import CORSMiddleware


load_dotenv(override=True)

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

client = AzureOpenAI(
    api_key=api_key,
    api_version="2024-10-01-preview",
    azure_endpoint=endpoint
)

app = FastAPI(title="Support Ticket API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # allow all origins (dev mode)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------
# Email Validator
# -------------------------
def is_valid_email(email: str) -> bool:
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None


# -------------------------
# Ticket Writer
# -------------------------
def submit_support_ticket(email, description):

    script_dir = Path(__file__).parent

    tickets_dir = script_dir / "tickets"
    tickets_dir.mkdir(exist_ok=True)

    ticket_number = str(uuid.uuid4()).replace("-", "")[:6]
    file_name = f"ticket-{ticket_number}.txt"
    file_path = tickets_dir / file_name

    text = (
        f"Support ticket: {ticket_number}\n"
        f"Submitted by: {email}\n"
        f"Description:\n{description}"
    )

    file_path.write_text(text, encoding="utf-8")

    return {
        "ticket_number": ticket_number,
        "file_name": file_name,
        "file_path": str(file_path),
        "email": email,
        "issue": description
    }


# -------------------------
# API Input Model
# -------------------------
class TicketRequest(BaseModel):
    email: str
    issue: str


# -------------------------
# API Endpoint
# -------------------------
@app.post("/create-ticket")
def create_ticket(req: TicketRequest):

    # Validate email
    if not is_valid_email(req.email):
        raise HTTPException(status_code=400, detail="Invalid email address")

    if not req.issue.strip():
        raise HTTPException(status_code=400, detail="Issue description is required")

    # Call Azure OpenAI to clean issue text
    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a support agent. "
                    "Return JSON like: {\"issue\":\"<cleaned issue>\"}"
                )
            },
            {"role": "user", "content": req.issue}
        ]
    )

    reply = response.choices[0].message.content

    try:
        data = json.loads(reply)
        issue_text = data.get("issue", req.issue)

    except Exception:
        issue_text = req.issue  # fallback if AI did not return JSON

    ticket = submit_support_ticket(req.email, issue_text)

    return {
        "status": "success",
        "message": "Ticket created successfully",
        "ticket": ticket
    }
#uvicorn AgentAPI:app --reload
