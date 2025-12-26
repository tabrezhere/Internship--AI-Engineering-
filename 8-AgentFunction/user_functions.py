from typing import Set, Callable, Any
import uuid
import json
from pathlib import Path


# Create a function to submit a support ticket
def submit_support_ticket(email_address: str, description: str) -> str:
    script_dir = Path(__file__).parent  # Get the directory of the script

    ticket_number = str(uuid.uuid4()).replace('-', '')[:6]
    file_name = f"ticket-{ticket_number}.txt"
    file_path = script_dir / file_name

    text = (
        f"Support ticket: {ticket_number}\n"
        f"Submitted by: {email_address}\n"
        f"Description:\n{description}"
    )

    file_path.write_text(text)

    message_json = json.dumps({
        "message": (
            f"Support ticket {ticket_number} submitted. "
            f"The ticket file is saved as {file_name}"
        )
    })

    return message_json

    
# Define callable function set
user_functions: Set[Callable[..., Any]] = {
    submit_support_ticket
}
