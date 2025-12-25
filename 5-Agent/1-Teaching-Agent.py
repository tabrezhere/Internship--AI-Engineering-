import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv(override=True)

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
)

# 🧠 AGENT DEFINITION
system_prompt = """
You are an AI Teaching Agent.

Your goal:
- Explain technical topics in simple language
- Give real-world examples
- Be clear and beginner-friendly
"""

def agent(question):
    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content


# 🧪 TEST
print(agent("Explain REST API in simple terms"))

