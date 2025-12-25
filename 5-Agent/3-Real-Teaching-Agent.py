import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from openai import AzureOpenAI

# Load env variables
load_dotenv(override=True)

app = FastAPI(title="AI Agent with Memory")

# Allow UI / browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Azure OpenAI Client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
)

# 🧠 SYSTEM PROMPT (Agent Rules)
SYSTEM_PROMPT = """
You are an AI Teaching Agent.

Your job:
- Explain topics clearly
- Use simple language
- Remember past conversation
"""

# 🧠 MEMORY (In-Memory Store)
chat_memory = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

@app.get("/chat")
def chat(q: str):
    # Add user message to memory
    chat_memory.append({"role": "user", "content": q})

    # Call Azure OpenAI
    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=chat_memory
    )

    answer = response.choices[0].message.content

    # Save assistant response
    chat_memory.append({"role": "assistant", "content": answer})

    return {
        "question": q,
        "answer": answer,
        "memory_size": len(chat_memory)
    }
# To run: uvicorn APIAgent_memory:app --reload

print("🧠 Why This Is a REAL Agent?")

print("\n✔ Has goal")
print("\n✔ Exposed as API")
print("\n✔ Reusable for UI / Mobile / Web")  
print("\n✔ Industry-style architecture") 

