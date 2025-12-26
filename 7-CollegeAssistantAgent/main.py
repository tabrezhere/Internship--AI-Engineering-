from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import AzureOpenAI, RateLimitError
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt
import os, io, base64, time

load_dotenv(override=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Azure OpenAI Client ----------
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# ---------- Load CSV Once ----------
df = pd.read_csv("students.csv")

# ---------- Simple In-Memory Cache ----------
CACHE = {}
CACHE_TTL = 300  # seconds (5 min)

def get_cache(key):
    if key in CACHE:
        value, ts = CACHE[key]
        if time.time() - ts < CACHE_TTL:
            return value
    return None

def set_cache(key, value):
    CACHE[key] = (value, time.time())

# ---------- Local Analytics (NO TOKENS) ----------
def subject_averages():
    return df[["sub1","sub2","sub3","sub4"]].mean().round(2).to_dict()

def pass_fail_count():
    return df["result"].value_counts().to_dict()

def generate_chart():
    avg = subject_averages()
    plt.figure()
    plt.bar(avg.keys(), avg.values())
    plt.title("Subject-wise Average Marks")

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)

    return base64.b64encode(buf.read()).decode()

# ---------- API ----------
@app.get("/analyze")
def analyze(query: str):

    # 1️⃣ Check cache first (0 tokens)
    cached = get_cache(query)
    if cached:
        return cached

    avg = subject_averages()
    pf = pass_fail_count()
    chart = generate_chart()

    # 2️⃣ VERY SHORT PROMPT (token-friendly)
    prompt = f"""
    Data:
    averages={avg}
    pass_fail={pf}

    Question: {query}
    Answer briefly.
    """

    try:
        response = client.chat.completions.create(
            model=DEPLOYMENT,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=120   # 🔥 HARD TOKEN LIMIT
        )
        explanation = response.choices[0].message.content

    except RateLimitError:
        explanation = (
            "Quota limit reached. Showing computed results.\n\n"
            f"Averages: {avg}\n"
            f"Pass/Fail: {pf}"
        )

    result = {
        "answer": explanation,
        "averages": avg,
        "pass_fail": pf,
        "chart": chart
    }

    # 3️⃣ Save to cache
    set_cache(query, result)

    return result
