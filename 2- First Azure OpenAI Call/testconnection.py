from openai import AzureOpenAI

client = AzureOpenAI(
    api_key="",
    azure_endpoint="",
    api_version="",
)

models = client.models.list()
print("CONNECTED")
