from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from openai import AzureOpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(override=True)

# Debug (optional – remove after verification)
print("DEPLOYMENT:", os.getenv("AZURE_OPENAI_DEPLOYMENT"))
print("ENDPOINT:", os.getenv("AZURE_OPENAI_ENDPOINT"))

# Initialize FastAPI
app = FastAPI(title="Hospital Assistant API")

# Enable CORS (for UI integration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # 🔴 change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Azure OpenAI Client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

@app.get("/ask")
def ask(q: str = Query(..., min_length=3)):
    system_prompt = """
    You are a Hospital Assistant AI.

    Your responsibilities:
    - Assist patients and hospital visitors
    - Explain medical terms in simple language
    - Guide on OPD, ICU, admissions, billing, insurance
    - Provide general health guidance (no diagnosis)
    - Recommend consulting doctors when needed

    Rules:
    - Do NOT diagnose diseases
    - Do NOT prescribe medicines
    - Be empathetic and professional
    - Keep answers clear and patient-friendly
    """

    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": q}
        ],
        temperature=0.3,
        max_tokens=400
    )

    return {
        "assistant": "Hospital Assistant",
        "answer": response.choices[0].message.content.strip()
    }
