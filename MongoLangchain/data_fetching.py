from langchain_community.chat_models import ChatOpenAI  # Updated import for LangChain >=0.2
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
import json
import pymongo
import os
import ast
from .config import ConfigData
from dotenv import load_dotenv

load_dotenv()

openai_api = os.getenv("OPENAI_API_KEY")
MONGO_DB_URI = os.getenv("MONGO_DB_URI")

# ----------------------------
# Initialize OpenAI LLM
# ----------------------------
llm_openai = ChatOpenAI(
    openai_api_key=openai_api,
    model='gpt-3.5-turbo-0125'
)

# ----------------------------
# Few-shot examples for prompt (double curly braces to avoid template issues)
# ----------------------------
json_ex_1 = [
    ConfigData.FEW_SHOT_EXAMPLE_1,
    ConfigData.FEW_SHOT_EXAMPLE_2,
    ConfigData.FEW_SHOT_EXAMPLE_3,
    ConfigData.FEW_SHOT_EXAMPLE_4
]

json_ex_string = json.dumps(json_ex_1, indent=2).replace("{", "{{").replace("}", "}}")

# ----------------------------
# Prompt Template
# ----------------------------
prompt_template_for_creating_query = f"""
You are an expert in crafting MongoDB NoSQL aggregation pipelines with 10 years of experience.
You will be provided with a table schema and a schema description. Your task is to read the user's question
and generate a valid MongoDB aggregation pipeline in JSON format.

Table Schema:
{ConfigData.TABLE_SCHEMA}

Schema Description:
{ConfigData.SCHEMA_DESCRIPTION}

Few-Shot Examples:
{json_ex_string}

Instructions:
- Only return the MongoDB aggregation pipeline (JSON array), nothing else.
- Do not include explanations or extra text.
- Use proper MongoDB syntax ($match, $project, $elemMatch, etc.) based on the question.

User Question: {{user_question}}
"""

query_creation_prompt = PromptTemplate(
    template=prompt_template_for_creating_query,
    input_variables=["user_question"]
)

# ----------------------------
# LLMChain
# ----------------------------
llmchain = LLMChain(llm=llm_openai, prompt=query_creation_prompt, verbose=True)

# ----------------------------
# Function to generate MongoDB pipeline
# ----------------------------
def get_query(user_question):
    response_text = llmchain.run(user_question=user_question)
    if not response_text or response_text.strip() == "":
        return json.dumps({"error": "LLM returned an empty response"})

    # --- 2. Clean code block markers ---
    response_text = response_text.strip()
    if response_text.startswith("```"):
        response_text = "\n".join(response_text.split("\n")[1:-1])

    try:
        pipeline = json.loads(response_text)
    except json.JSONDecodeError:
        try:
            pipeline = ast.literal_eval(response_text)  
        except Exception:
            return json.dumps({"error": f"Invalid response: {response_text}"})

    result = collection.aggregate(pipeline)
    docs = [doc for doc in result]

    if not docs:
        return json.dumps({"data": "No results found in the database"})
    return json.dumps(docs, indent=2)

# ----------------------------
# MongoDB Connection
# ----------------------------
client = pymongo.MongoClient(MONGO_DB_URI)
db = client[ConfigData.DB_NAME]
collection = db[ConfigData.COLLECTION_NAME]


