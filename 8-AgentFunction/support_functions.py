import os
import re
import uuid
from pathlib import Path

# -------------------------
# Validate Email
# -------------------------
def is_valid_email(email: str) -> bool:
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None


# -------------------------
# Support Ticket Writer
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
# Email Preview (No Send)
# -------------------------
def send_ticket_email(ticket):

    gmail_user = os.getenv("GMAIL_ADDRESS")
    to_email = os.getenv("NOTIFY_TO_EMAIL") or gmail_user

    subject = f"New Support Ticket #{ticket['ticket_number']}"

    print("\n------ Email Preview (Not Sent) ------")
    print(f"From   : {gmail_user}")
    print(f"To     : {to_email}")
    print(f"Subject: {subject}")
    print("--------------------------------------")
    print("Body:")
    print(f"Ticket Number : {ticket['ticket_number']}")
    print(f"Submitted By  : {ticket['email']}")
    print("")
    print("Issue:")
    print(ticket['issue'])
    print("")
    print("Ticket File:")
    print(ticket['file_path'])
    print("--------------------------------------")
    print("📩 Email sending disabled (preview mode only).")
    print("--------------------------------------\n")
