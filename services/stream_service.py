from openai import OpenAI
from risen_ai.core.config import settings
from risen_ai.core.prompts import RISEN_SYSTEM_PROMPT
from risen_ai.knowledge_base.retriever import retrieve_context
from risen_ai.services.memory_service import get_history, add_message

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def stream_ai_response(user_message: str, mode: str, session_id: str):

    context = retrieve_context(user_message)
    history = get_history(session_id)

    mode_instruction = {
        "education": "Explain clearly like a teacher.",
        "market": "Respond like a smart-money analyst.",
        "risen": "Respond as RISEN ecosystem expert.",
        "content": "Write engaging, viral-style content.",
        "default": "Respond normally."
    }

    messages = [
        {"role": "system", "content": RISEN_SYSTEM_PROMPT},
        {"role": "system", "content": f"Mode: {mode}. {mode_instruction.get(mode)}"},
        {"role": "system", "content": f"Context:\n{context}"}
    ]

    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    stream = client.chat.completions.create(
        model=settings.MODEL,
        messages=messages,
        temperature=settings.TEMPERATURE,
        stream=True
    )

    full_response = ""

    for chunk in stream:
        delta = chunk.choices[0].delta.content

        if delta:
            full_response += delta
            yield delta

    # 🔥 save after complete
    add_message(session_id, "user", user_message)
    add_message(session_id, "assistant", full_response)