from dotenv import load_dotenv
from pathlib import Path

from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings,
    ChatGoogleGenerativeAI
)

from langchain_qdrant import QdrantVectorStore

# ==================================================
# LOAD ENV
# ==================================================

load_dotenv(
    Path(__file__).parent.parent / ".env"
)

# ==================================================
# EMBEDDING MODEL
# ==================================================

embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

# ==================================================
# VECTOR STORE
# ==================================================

import os

import os

print("QDRANT_URL =", os.getenv("QDRANT_URL"))
print("QDRANT_API_KEY EXISTS =", bool(os.getenv("QDRANT_API_KEY")))
print("GOOGLE_API_KEY EXISTS =", bool(os.getenv("GOOGLE_API_KEY")))

vector_db = QdrantVectorStore.from_existing_collection(
    embedding=embedding_model,
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
    collection_name="learning_vectors"
)

# ==================================================
# LLM
# ==================================================

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.2
)

# ==================================================
# ASK QUESTION
# ==================================================

def ask_question(
    query,
    chat_history=None
):

    docs = vector_db.max_marginal_relevance_search(
        query=query,
        k=8,
        fetch_k=40
    )

    context = "\n\n".join(
        [
            f"""
PAGE:
{doc.metadata.get('page', 0) + 1}

CONTENT:
{doc.page_content}
"""
            for doc in docs
        ]
    )

    system_prompt = f"""
You are a PDF RAG Assistant.

RULES:

1. Use ONLY the provided context.
2. Mention page numbers.
3. Never hallucinate.
4. Never use outside knowledge.
5. If answer is unavailable say:

'I could not find that information in the document.'

6. Keep answers concise.

CONTEXT:

{context}
"""

    messages = [
        ("system", system_prompt)
    ]

    if chat_history:

        for msg in chat_history:

            if msg["role"] == "user":

                messages.append(
                    ("human", msg["content"])
                )

            elif msg["role"] == "assistant":

                messages.append(
                    ("ai", msg["content"])
                )

    messages.append(
        ("human", query)
    )

    response = llm.invoke(
        messages
    )

    return (
        response.content,
        docs
    )