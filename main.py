from dotenv import load_dotenv
from pathlib import Path
import time

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore


import os

load_dotenv(
    Path(__file__).parent.parent / ".env"
)

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")


PDF_PATH = Path(__file__).parent / "nodejs.pdf"

COLLECTION_NAME = "learning_vectors"


BATCH_SIZE = 5

print("\nLoading PDF...")

loader = PyPDFLoader(str(PDF_PATH))

docs = loader.load()

print(f"Pages Loaded: {len(docs)}")

print("\nCreating Chunks...")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

split_docs = text_splitter.split_documents(docs)

print(f"Chunks Created: {len(split_docs)}")

print("\nLoading Gemini Embeddings...")

embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

print("\nCreating Qdrant Collection...")

vector_store = QdrantVectorStore.from_documents(
    documents=split_docs[:BATCH_SIZE],
    embedding=embedding_model,
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    collection_name=COLLECTION_NAME
)

print(
    f"Uploaded {BATCH_SIZE}/{len(split_docs)}"
)

for i in range(
    BATCH_SIZE,
    len(split_docs),
    BATCH_SIZE
):

    batch = split_docs[
        i:i + BATCH_SIZE
    ]

    try:

        vector_store.add_documents(
            batch
        )

        uploaded = min(
            i + BATCH_SIZE,
            len(split_docs)
        )

        print(
            f"Uploaded {uploaded}/{len(split_docs)}"
        )

        time.sleep(2)

    except Exception as e:

        print(
            f"\nFailed at batch {i}"
        )

        print(e)

        break

print("\nVerifying Collection...")

try:

    results = vector_store.similarity_search(
        "What is Node.js?",
        k=3
    )

    print(
        f"Retrieved {len(results)} chunks"
    )

except Exception as e:

    print(e)

print("\nIndexing Complete!")