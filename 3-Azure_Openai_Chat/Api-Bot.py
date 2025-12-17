from fastapi import FastAPI
from openai import AzureOpenAI
from dotenv import load_dotenv
import os
load_dotenv(override=True)

print("KEY:", os.getenv("AZURE_OPENAI_API_KEY"))
print("ENDPOINT:", os.getenv("AZURE_OPENAI_ENDPOINT"))
print("DEPLOYMENT:", os.getenv("AZURE_OPENAI_DEPLOYMENT"))


app = FastAPI()
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

@app.get("/ask")
def ask(q: str):
    res = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=[{"role": "user", "content": q}]
    )
    return {"answer": res.choices[0].message.content}
#uvicorn Api-Bot:app --reload
