import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv(override=True)

# --- Azure OpenAI Client ---
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
)

DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

print("USING DEPLOYMENT:", DEPLOYMENT)
print("ENDPOINT:", os.getenv("AZURE_OPENAI_ENDPOINT"))


def call_model(messages):
    response = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=messages,
        temperature=0.3
    )
    return response.choices[0].message.content


# --------------------------
# Agent A — Intent Identifier
# --------------------------

intent_agent_system = """
You are an Intent Classifier Agent.

Identify which domain the query belongs to.

Return only one of:
- billing
- loan
- sim_network

Also give a short reason.
"""


def detect_intent(user_query):
    messages = [
        {"role": "system", "content": intent_agent_system},
        {"role": "user", "content": user_query}
    ]
    return call_model(messages)


# --------------------------
# Domain Agents
# --------------------------

billing_agent = """
You are Billing Domain Agent.
Explain billing issues clearly and politely.
"""

loan_agent = """
You are Loan Eligibility Agent.
Explain eligibility in simple and helpful terms.
"""

sim_agent = """
You are SIM & Network Support Agent.
Provide troubleshooting steps and guidance.
"""


def run_domain_agent(agent_system_prompt, user_query):
    messages = [
        {"role": "system", "content": agent_system_prompt},
        {"role": "user", "content": user_query}
    ]
    return call_model(messages)


# --------------------------
# Dispatcher Logic
# --------------------------

def route_to_domain_agent(intent_text, user_query):

    text = intent_text.lower()

    if "billing" in text:
        return run_domain_agent(billing_agent, user_query)

    if "loan" in text:
        return run_domain_agent(loan_agent, user_query)

    if "sim" in text or "network" in text:
        return run_domain_agent(sim_agent, user_query)

    return "Sorry, I could not determine the right support category."


# --------------------------
# Interactive Loop
# --------------------------

print("\n--- Multi-Agent Support Assistant ---")
print("Type your question below.")
print("Type 'exit' to quit.\n")

while True:

    user_message = input("You: ").strip()

    if user_message.lower() in ["exit", "quit", "q"]:
        print("\nExiting. Goodbye 👋")
        break

    print("\nAgent-A (Intent Identifier) 🎯")
    intent_result = detect_intent(user_message)
    print(intent_result)

    print("\nRouting to appropriate Domain Agent...\n")
    final_response = route_to_domain_agent(intent_result, user_message)

    print("Domain Agent Response 🤖")
    print(final_response)
    print("\n------------------------------------\n")
