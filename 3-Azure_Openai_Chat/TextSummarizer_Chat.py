import os
from dotenv import load_dotenv
from openai import AzureOpenAI
load_dotenv(override=True)

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
)

text = """
Artificial Intelligence (AI) is a branch of computer science that focuses on creating machines and software capable of performing tasks that normally require human intelligence. These tasks include understanding language, recognizing images and speech, learning from data, solving problems, and making decisions. Unlike traditional programs that follow fixed rules written by a developer, AI systems can analyze large amounts of data, identify patterns, and improve their performance over time based on experience. AI is widely used in everyday applications such as chatbots, recommendation systems, navigation apps, face recognition, and fraud detection. By enabling machines to think, learn, and act intelligently, AI helps automate complex processes, increases efficiency, and supports better decision-making across industries like healthcare, education, finance, and software development
"""

prompt = f"Summarize the following text in one sentence:\n{text}"

response = client.chat.completions.create(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    messages=[{"role": "user", "content": prompt}]
)

print(response.choices[0].message.content)
