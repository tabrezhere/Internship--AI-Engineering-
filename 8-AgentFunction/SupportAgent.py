import os
import json
import uuid
import re
from pathlib import Path
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv(override=True)

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

client = AzureOpenAI(
    api_key=api_key,
    api_version="2024-10-01-preview",
    azure_endpoint=endpoint
)


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
        "file_path": str(file_path)
    }


def is_valid_email(email: str) -> bool:
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None


print("\nSupport Agent Ready (Email Required)\n")


while True:

    # --- Get Email (Mandatory) ---
    while True:
        email = input("Enter your email address (or type quit): ").strip()

        if email.lower() == "quit":
            exit()

        if not email:
            print("Email is required. Please enter a valid email.\n")
            continue

        if not is_valid_email(email):
            print("Invalid email format. Please enter a valid email.\n")
            continue

        break

    # --- Get Issue Description ---
    issue = input("Enter your issue description: ").strip()

    if not issue:
        print("Issue description cannot be empty.\n")
        continue

    # --- Ask AI to summarize issue if useful ---
    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a support assistant. "
                    "Return JSON in the format:\n"
                    "{\"issue\":\"<cleaned issue description>\"}"
                )
            },
            {"role": "user", "content": issue}
        ]
    )

    reply = response.choices[0].message.content

    try:
        data = json.loads(reply)
        issue_text = data.get("issue", issue)

        result = submit_support_ticket(email, issue_text)

        print("\nTicket Created Successfully")
        print("---------------------------")
        print("Ticket No :", result["ticket_number"])
        print("User Email:", email)
        print("File Name :", result["file_name"])
        print("Saved At  :", result["file_path"], "\n")

    except Exception:
        # Fallback — still save ticket even if AI reply is not JSON
        result = submit_support_ticket(email, issue)

        print("\nTicket Created (AI JSON Parse Failed — Saved Raw Issue)")
        print("Ticket No :", result["ticket_number"])
        print("Saved At  :", result["file_path"], "\n")
