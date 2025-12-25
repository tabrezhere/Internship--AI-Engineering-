import os
from dotenv import load_dotenv
from pathlib import Path
from openai import AzureOpenAI

# Load environment variables
load_dotenv(override=True)

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

if not endpoint or not api_key or not deployment:
    raise ValueError("Missing required environment values in .env")


# Create client using API KEY (Inference endpoint)
client = AzureOpenAI(
    api_key=api_key,
    api_version="2024-06-01",
    azure_endpoint=endpoint
)


def load_data():
    script_dir = Path(__file__).parent
    file_path = script_dir / "data.txt"

    if not file_path.exists():
        raise FileNotFoundError("data.txt not found in script folder")

    with file_path.open("r", encoding="utf-8") as f:
        data = f.read()

    print("\n===== Loaded Data =====\n")
    print(data)
    print("\n=======================\n")

    return data


def ask_model(system_prompt, user_prompt):
    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )

    return response.choices[0].message.content


def main():

    os.system('cls' if os.name == 'nt' else 'clear')

    data = load_data()

    system_prompt = (
        "You are a data analysis assistant. "
        "You analyze the provided dataset text, compute statistics, "
        "summaries and insights when requested."
    )

    print("Type questions about the dataset.")
    print("Example: summarize, calculate averages, detect trends")
    print("Type 'quit' to exit.\n")

    while True:
        user_input = input("Ask a question: ")

        if user_input.lower().strip() == "quit":
            break

        if not user_input.strip():
            print("Please enter a question.")
            continue

        prompt = f"Here is the dataset:\n\n{data}\n\nUser question: {user_input}"

        answer = ask_model(system_prompt, prompt)

        print("\n--- Model Response ---\n")
        print(answer)
        print("\n----------------------\n")


if __name__ == "__main__":
    main()
