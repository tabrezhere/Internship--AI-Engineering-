import os
import json
import asyncio
import pandas as pd
from dotenv import load_dotenv

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.functions import KernelFunctionFromPrompt, KernelPlugin


# ---------------- Load ENV ----------------
load_dotenv(override=True)

AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")


# ---------------- Kernel + Azure Setup ----------------
kernel = sk.Kernel()

chat_service = AzureChatCompletion(
    deployment_name=AZURE_DEPLOYMENT,
    api_key=AZURE_KEY,
    endpoint=AZURE_ENDPOINT
)

kernel.add_service(chat_service)

print("Azure OpenAI Connected ✔")


# ---------------- Create Plugin WITH functions ----------------
plugin = KernelPlugin(
    name="task_agent",
    functions=[

        # ---- Function 1 : Task Parser ----
        KernelFunctionFromPrompt.from_prompt(
            prompt="""
From this instruction, extract:

- product_name
- product_file
- person_name
- details_file

Return ONLY JSON in this format:
{
 "product_name": "",
 "product_file": "",
 "person_name": "",
 "details_file": ""
}

Instruction:
{{$input}}
""",
            plugin_name="task_agent",
            function_name="task_parser"
        ),

        # ---- Function 2 : Email Template ----
        KernelFunctionFromPrompt.from_prompt(
            prompt="""
Write a short professional email to ${email}
containing the following product details:

{{$input}}
""",
            plugin_name="task_agent",
            function_name="email_template"
        )
    ]
)

# -------- Register plugin in kernel --------
kernel.add_plugin(plugin)


# ---------------- CSV Helpers ----------------
def get_product_details(product_name, csv_file):
    if not os.path.exists(csv_file):
        print(f"❌ File not found: {csv_file}")
        return None

    df = pd.read_csv(csv_file)
    row = df[df["product"].str.lower() == product_name.lower()]
    return None if row.empty else row.iloc[0].to_dict()


def get_person_details(person_name, csv_file):
    if not os.path.exists(csv_file):
        print(f"❌ File not found: {csv_file}")
        return None

    df = pd.read_csv(csv_file)
    row = df[df["name"].str.lower() == person_name.lower()]
    return None if row.empty else row.iloc[0].to_dict()


# ---------------- Sequential Agent Engine ----------------
async def run_agent(user_prompt):

    print("\n📝 USER PROMPT:")
    print(user_prompt)

    task_parser_fn = kernel.get_function("task_agent", "task_parser")

    # ---- Step 1 — Understand Task ----
    parsed = await kernel.invoke(
        task_parser_fn,
        input=user_prompt
    )

    print("\n🔍 PARSED TASK JSON:")
    print(parsed)

    task = json.loads(str(parsed))

    product_name = task["product_name"]
    product_file = task["product_file"]
    person_name = task["person_name"]
    details_file = task["details_file"]

    # ---- Step 2 — Fetch Product ----
    product_info = get_product_details(product_name, product_file)

    if not product_info:
        print("\n⚠ Product not found in CSV")
        return

    print("\n📦 PRODUCT DATA:")
    print(product_info)

    # ---- Step 3 — Fetch Recipient ----
    person_info = get_person_details(person_name, details_file)

    if not person_info:
        print("\n⚠ Person not found in CSV")
        return

    print("\n👤 RECIPIENT DATA:")
    print(person_info)

    # ---- Step 4 — Generate Email ----
    email_fn = kernel.get_function("task_agent", "email_template")

    email_body = await kernel.invoke(
        email_fn,
        input=str(product_info),
        email=person_info["email"]
    )

    print("\n📧 EMAIL GENERATED:")
    print(email_body)

    print("\n✅ TASK EXECUTED SEQUENTIALLY")


# ---------------- Run Example ----------------
if __name__ == "__main__":

    prompt = """
    can you get the apple details from product.csv
    and send to Ahmed using details.csv
    """

    asyncio.run(run_agent(prompt))
