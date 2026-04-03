from risen_ai.knowledge_base.vector_store import get_vector_store

def retrieve_context(query: str):

    vector_store = get_vector_store()

    docs = vector_store.similarity_search(query, k=4)

    return "\n\n".join([doc.page_content for doc in docs])