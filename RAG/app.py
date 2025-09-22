import os
import sys
from operator import itemgetter
from typing import List
from typing_extensions import TypedDict

from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_core.pydantic_v1 import BaseModel, Field
from langgraph.graph import END, StateGraph
import streamlit as st

# Add parent directory to path to import MongoLangchain
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MongoLangchain.data_fetching import get_query

# Load environment variables
load_dotenv()

# === Initialize Models & Stores ===
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large",
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# Pinecone setup
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
index = pc.Index(os.environ.get("PINECONE_INDEX_NAME"))
vector_store = PineconeVectorStore(index=index, embedding=embeddings)

# Retriever
retriever = vector_store.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"k": 2, "score_threshold": 0.7},
)

# === Document Grading ===
class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""
    binary_score: str = Field(
        description="Documents are relevant to the question, 'yes' or 'no'"
    )

llm_grader = llm.with_structured_output(GradeDocuments)

SYS_PROMPT = """You are an expert grader assessing relevance of a retrieved document to a user question.
- If the document contains keyword(s) or semantic meaning related to the question, grade it as relevant.
- Output 'yes' or 'no' only.
"""

grade_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYS_PROMPT),
        ("human", "Retrieved document:\n{document}\n\nUser question:\n{question}"),
    ]
)
grader_chain = grade_prompt | llm_grader

# === RAG Prompt ===
rag_prompt = ChatPromptTemplate.from_template(
    """You are an assistant for question-answering tasks.
Use the retrieved context to answer the question.
If no relevant context is available or Data not found in the database, say you don't know.

Question: {question}
Context: {context}
Answer:"""
)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {
        "context": itemgetter("context") | RunnableLambda(format_docs),
        "question": itemgetter("question"),
    }
    | rag_prompt
    | llm
    | StrOutputParser()
)

# === Graph State ===
class GraphState(TypedDict):
    question: str
    generation: str
    database_search_needed: str
    documents: List[Document]

# === Graph Nodes ===
def retrieve(state: GraphState):
    question = state["question"]
    documents = retriever.invoke(question)
    return {"documents": documents, "question": question}

def grade_documents(state: GraphState):
    question = state["question"]
    documents = state["documents"]

    filtered_docs = []
    database_search_needed = "No"

    for d in documents or []:
        score = grader_chain.invoke({"question": question, "document": d.page_content})
        if score.binary_score == "yes":
            filtered_docs.append(d)
        else:
            database_search_needed = "Yes"

    if not documents:
        database_search_needed = "Yes"

    return {"documents": filtered_docs, "question": question,
            "database_search_needed": database_search_needed}

def database_search(state: GraphState):
    question = state["question"]
    documents = state["documents"]

    db_docs = get_query(user_question=question)
    if db_docs:
        db_content = "\n\n".join(db_docs) 
        documents.append(Document(page_content=db_content))

    return {"documents": documents, "question": question}

def generate_answer(state: GraphState):
    question = state["question"]
    documents = state["documents"]

    generation = rag_chain.invoke({"context": documents, "question": question})
    return {"documents": documents, "question": question, "generation": generation}

def decide_to_generate(state: GraphState):
    return "database_search" if state["database_search_needed"] == "Yes" else "generate_answer"

# === Build Graph ===
agentic_rag = StateGraph(GraphState)
agentic_rag.add_node("retrieve", retrieve)
agentic_rag.add_node("grade_documents", grade_documents)
agentic_rag.add_node("database_search", database_search)
agentic_rag.add_node("generate_answer", generate_answer)

agentic_rag.set_entry_point("retrieve")
agentic_rag.add_edge("retrieve", "grade_documents")
agentic_rag.add_conditional_edges(
    "grade_documents", decide_to_generate,
    {"database_search": "database_search", "generate_answer": "generate_answer"},
)
agentic_rag.add_edge("database_search", "generate_answer")
agentic_rag.add_edge("generate_answer", END)

agentic_rag = agentic_rag.compile()

# === Run Query ===
# if __name__ == "__main__":
#     query = "What is Sewana Hospital ?"
#     response = agentic_rag.invoke({"question": query})
#     print(response['generation'])


# ----------------------------
# Streamlit UI
# ----------------------------

st.set_page_config(page_title="Sewana Hospital QA", layout="wide")


st.title("🏥 Sewana Hospital QA Assistant")
st.write("Ask any question about Sewana Hospital and get instant answers.")

# --- User Input ---
question = st.text_input("Enter your question:")

# --- Layout for button and answer ---
if st.button("Get Answer"):
    if question.strip() == "":
        st.warning("⚠️ Please enter a question!")
    else:
        with st.spinner("🔍 Retrieving and generating answer..."):
            response = agentic_rag.invoke({"question": question})
        
        # --- Display Answer in a nice container ---
        st.subheader("Answer")
        answer_text = response.get("generation", "No answer generated.")
        st.success(answer_text)

# Optional: Add some spacing and visual structure
st.markdown("---")
st.info("💡 Tip: Ask questions like 'What are the visiting hours?' or 'How can I book an appointment?'")