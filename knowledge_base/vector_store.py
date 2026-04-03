from langchain_chroma import Chroma
from knowledge_base.embeddings import get_embeddings
from core.config import settings

def get_vector_store():
    return Chroma(
        persist_directory=settings.VECTOR_DB_PATH,
        embedding_function=get_embeddings()
    )