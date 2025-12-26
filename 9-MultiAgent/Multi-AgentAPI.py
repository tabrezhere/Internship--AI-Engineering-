import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import AzureOpenAI

load_dotenv(override=True)

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
)

DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

app = FastAPI(title="Multi-Agent Support System")

# Allow browser UI calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def call_model(messages):
    response = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=messages,
        temperature=0.3
    )
    return response.choices[0].message.content


# ---------- Agent Prompts ----------

intent_agent_system = """
You are an Intent Classifier Agent.
Return the domain:

billing
loan
sim_network

Also include a short reason.
"""

billing_agent = "You are Billing Agent. Explain billing issues clearly."
loan_agent = "You are Loan Eligibility Agent. Explain eligibility simply."
sim_agent = "You are SIM & Network Agent. Provide troubleshooting steps."


def detect_intent(user_query: str):
    return call_model([
        {"role": "system", "content": intent_agent_system},
        {"role": "user", "content": user_query}
    ])


def run_domain_agent(agent_prompt: str, user_query: str):
    return call_model([
        {"role": "system", "content": agent_prompt},
        {"role": "user", "content": user_query}
    ])


def route_to_domain_agent(intent_text: str, user_query: str):
    text = intent_text.lower()

    if "billing" in text:
        agent = "billing"
        reply = run_domain_agent(billing_agent, user_query)

    elif "loan" in text:
        agent = "loan"
        reply = run_domain_agent(loan_agent, user_query)

    elif "sim" in text or "network" in text:
        agent = "sim_network"
        reply = run_domain_agent(sim_agent, user_query)

    else:
        agent = "unknown"
        reply = "Sorry, I could not determine the right support category."

    return {
        "domain_agent": agent,
        "response": reply
    }


# ---------- API Schema ----------

class QueryRequest(BaseModel):
    query: str


# ---------- API Endpoint ----------

@app.post("/ask")
def ask_agent(request: QueryRequest):

    intent_result = detect_intent(request.query)

    routed = route_to_domain_agent(
        intent_text=intent_result,
        user_query=request.query
    )

    return {
        "user_query": request.query,
        "intent_result": intent_result,
        **routed
    }
