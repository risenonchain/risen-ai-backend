from langchain_openai import OpenAIEmbeddings
from core.config import settings

def get_embeddings():
    return OpenAIEmbeddings(
        api_key=settings.OPENAI_API_KEY
    )