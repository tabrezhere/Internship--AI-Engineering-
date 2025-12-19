from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from openai import AzureOpenAI
from dotenv import load_dotenv
import os

load_dotenv(override=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# ✅ Chat history
chat_history = [
    {"role": "system", "content": "You are a helpful assistant."}
]

@app.get("/ask")
def ask(q: str = Query(..., min_length=1)):
    # 1️⃣ Add user message
    chat_history.append({"role": "user", "content": q})

    # 2️⃣ Send full history to model
    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=chat_history
    )

    answer = response.choices[0].message.content

    # 3️⃣ Add assistant response
    chat_history.append({"role": "assistant", "content": answer})

    return {
        "question": q,
        "answer": answer,
        "history_length": len(chat_history)
    }
