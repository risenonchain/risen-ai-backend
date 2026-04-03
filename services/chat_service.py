from openai import OpenAI
from risen_ai.core.config import settings
from risen_ai.core.prompts import RISEN_SYSTEM_PROMPT
from risen_ai.knowledge_base.retriever import retrieve_context
from risen_ai.services.memory_service import get_history, add_message

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def get_ai_response(user_message: str, mode: str = "default", session_id: str = "default"):

    context = retrieve_context(user_message)

    history = get_history(session_id)

    mode_instruction = {
        "education": "Explain clearly using structured steps and simple breakdowns.",
        "market": "Provide structured analysis with bullet points and key insights.",
        "risen": "Explain RISEN clearly with sections and concise structure.",
        "content": "Write concise, punchy, shareable content.",
        "default": "Respond clearly using headings and bullet points."
    }

    messages = [
        {"role": "system", "content": RISEN_SYSTEM_PROMPT},
        {"role": "system", "content": f"Mode: {mode}. {mode_instruction.get(mode)}"},
        {"role": "system", "content": f"Context:\n{context}"}
    ]

    # 🔥 ADD MEMORY
    messages.extend(history)

    # Add current user message
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model=settings.MODEL,
        messages=messages,
        temperature=settings.TEMPERATURE
    )

    reply = response.choices[0].message.content

    # 🔥 SAVE MEMORY
    add_message(session_id, "user", user_message)
    add_message(session_id, "assistant", reply)

    return reply