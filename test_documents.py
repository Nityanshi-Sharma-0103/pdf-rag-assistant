from dotenv import load_dotenv
from pathlib import Path

from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv(Path(__file__).parent.parent / ".env")

embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-2"
)

result = embedding_model.embed_documents(
    ["dummy_text"]
)

print(len(result[0]))