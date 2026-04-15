from knowledge_base.vector_store import get_vector_store


RISEN_KEYWORDS = [
    "risen", "$rsn", "risen ai", "risen rush", "risen foundation", "risen academy",
    "memecoin bridger", "dust sweeper", "tokenomics", "whitepaper", "litepaper", "roadmap"
]

def is_risen_prompt(query: str) -> bool:
    q = query.lower()
    return any(keyword in q for keyword in RISEN_KEYWORDS)

def retrieve_context(query: str):
    vector_store = get_vector_store()
    # Prioritize RISEN context for RISEN prompts
    if is_risen_prompt(query):
        docs = vector_store.similarity_search(query + " RISEN", k=6)
    else:
        docs = vector_store.similarity_search(query, k=4)
    return "\n\n".join([doc.page_content for doc in docs])

# Utility to reload vector store (for CLI/endpoint use)
def reload_vector_store():
    from .ingest import ingest_documents
    ingest_documents()
    print("✅ Vector store reloaded with latest .md files.")