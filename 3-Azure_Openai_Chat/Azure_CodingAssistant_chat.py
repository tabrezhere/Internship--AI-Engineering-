import os
from dotenv import load_dotenv
from openai import AzureOpenAI
load_dotenv(override=True)

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
)


messages = [
    {"role": "system", "content": "You are a coding mentor"},
    {"role": "user", "content": "Explain linked list with example"}
]

response = client.chat.completions.create(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    messages=messages
)

print(response.choices[0].message.content)
