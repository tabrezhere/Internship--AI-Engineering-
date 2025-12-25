import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv(override=True)

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
)

# 🧠 AGENT SYSTEM PROMPT
system_prompt = """
You are an AI Teaching Agent.

Rules:
- Explain concepts simply
- Use examples
- Remember previous conversation
"""

# 🧠 MEMORY (Chat History)
memory = [
    {"role": "system", "content": system_prompt}
]

def agent_with_memory(user_input):
    # Add user input to memory
    memory.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=memory
    )

    assistant_reply = response.choices[0].message.content

    # Save assistant response to memory
    memory.append({"role": "assistant", "content": assistant_reply})

    return assistant_reply


# 🧪 TEST CONVERSATION
print(agent_with_memory("Explain REST API"))
print("\n---\n")
print(agent_with_memory("Explain it again in simpler words"))
print("\n**************************************************\n")

print("🧠 What Is Happening Internally?")

print("\n✔ memory stores full conversation")
print("\n✔ Every request sends past + new messages")
print("\n✔ Model uses context awareness")  
print("\n✔ Agent behaves intelligently") 

