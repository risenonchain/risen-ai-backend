from openai import OpenAI
from core.config import settings
from core.prompts import RISEN_SYSTEM_PROMPT
from knowledge_base.retriever import retrieve_context
from services.memory_service import get_history, add_message

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def stream_ai_response(user_message: str, mode: str, session_id: str):

    try:
        context = retrieve_context(user_message)
    except Exception as e:
        print("⚠️ Context error:", str(e))
        context = ""

    history = get_history(session_id)

    # ✅ FIX: ensure history is list
    if not isinstance(history, list):
        print("⚠️ History not list, resetting...")
        history = []

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

    # ✅ SAFE EXTEND
    try:
        messages.extend(history)
    except Exception as e:
        print("🔥 EXTEND ERROR:", str(e))

    messages.append({"role": "user", "content": user_message})

    try:
        stream = client.chat.completions.create(
            model=settings.MODEL,
            messages=messages,
            temperature=settings.TEMPERATURE,
            stream=True
        )
    except Exception as e:
        print("🔥 OPENAI STREAM ERROR:", str(e))
        yield "⚠️ AI streaming failed."
        return

    full_response = ""

    try:
        for chunk in stream:
            try:
                delta = chunk.choices[0].delta

                # ✅ FIX: safe content access
                content = getattr(delta, "content", None)

                if content:
                    full_response += content
                    yield content

            except Exception as e:
                print("⚠️ Chunk error:", str(e))
                continue

    except Exception as e:
        print("🔥 STREAM LOOP ERROR:", str(e))
        yield "⚠️ Streaming interrupted."

    # 🔥 SAVE MEMORY (SAFE)
    try:
        add_message(session_id, "user", user_message)
        add_message(session_id, "assistant", full_response)
    except Exception as e:
        print("⚠️ Memory save error:", str(e))
