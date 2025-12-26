import os
import json
from dotenv import load_dotenv
from openai import AzureOpenAI

from support_functions import (
    is_valid_email,
    submit_support_ticket,
    send_ticket_email
)

# Load environment values
load_dotenv(override=True)

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

client = AzureOpenAI(
    api_key=api_key,
    api_version="2024-10-01-preview",
    azure_endpoint=endpoint
)


print("\nSupport Ticket Assistant (Azure OpenAI + Gmail)\n")


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

    # --- Ask AI to clean / summarize issue ---
    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a support agent. "
                    "Return JSON only in format:\n"
                    "{\"issue\":\"<cleaned issue>\"}"
                )
            },
            {"role": "user", "content": issue}
        ]
    )

    reply = response.choices[0].message.content

    try:
        data = json.loads(reply)
        issue_text = data.get("issue", issue)

    except Exception:
        issue_text = issue

    # --- Create Ticket File ---
    ticket = submit_support_ticket(email, issue_text)

    print("\nTicket Created Successfully")
    print("---------------------------")
    print("Ticket No :", ticket["ticket_number"])
    print("User Email:", ticket["email"])
    print("File Name :", ticket["file_name"])
    print("Saved At  :", ticket["file_path"], "\n")

    # --- Send Email Notification ---
    send_ticket_email(ticket)
