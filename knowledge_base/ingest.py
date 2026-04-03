import os

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from risen_ai.knowledge_base.vector_store import get_vector_store

DATA_PATH = "risen_ai/knowledge_base/data"

def ingest_documents():

    documents = []

    for file in os.listdir(DATA_PATH):
        if file.endswith(".md"):
            loader = TextLoader(os.path.join(DATA_PATH, file),encoding="utf-8")
            documents.extend(loader.load())

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    docs = splitter.split_documents(documents)

    vector_store = get_vector_store()
    vector_store.add_documents(docs)

    print("✅ RISEN knowledge base ingested successfully")


if __name__ == "__main__":
    ingest_documents()