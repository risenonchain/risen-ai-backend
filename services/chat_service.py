from openai import OpenAI
from core.config import settings
from core.prompts import RISEN_SYSTEM_PROMPT
from knowledge_base.retriever import retrieve_context
from services.memory_service import get_history, add_message

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def get_ai_response(
    user_message: str,
    mode: str = "default",
    session_id: str = "default",
    context: dict = {}  # 🔥 NEW
):

    context_data = retrieve_context(user_message)
    history = get_history(session_id)

    mode_instruction = {
        "education": "Explain clearly using structured steps and simple breakdowns.",
        "market": "Provide structured analysis with bullet points and key insights.",
        "risen": "Explain RISEN clearly with sections and concise structure.",
        "content": "Write concise, punchy, shareable content.",
        "default": "Respond clearly using headings and bullet points."
    }

    # 🔥 USER CONTEXT STRING
    user_context = ""
    if context:
        user_context = f"User Context:\n{context}"

    messages = [
        {"role": "system", "content": RISEN_SYSTEM_PROMPT},
        {"role": "system", "content": f"Mode: {mode}. {mode_instruction.get(mode)}"},
        {"role": "system", "content": f"Knowledge Context:\n{context_data}"},
        {"role": "system", "content": user_context}  # 🔥 NEW
    ]

    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model=settings.MODEL,
        messages=messages,
        temperature=settings.TEMPERATURE
    )

    reply = response.choices[0].message.content

    add_message(session_id, "user", user_message)
    add_message(session_id, "assistant", reply)

    return reply