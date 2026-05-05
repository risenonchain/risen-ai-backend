from openai import OpenAI
from core.config import settings
from core.prompts import RISEN_SYSTEM_PROMPT
from knowledge_base.retriever import retrieve_context
from services.memory_service import get_history, add_message

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def stream_ai_response(user_message: str, mode: str, session_id: str):
    try:
        context = retrieve_context(user_message)
    except:
        context = ""

    history = get_history(session_id)
    if not isinstance(history, list):
        history = []

    mode_instruction = {
        "education": "Protocol: Lead Educator. Break down complex cryptosystems into digestible logical blocks.",
        "market": "Protocol: Strategic Analyst. Focus on high-signal market intelligence and structural trends.",
        "risen": "Protocol: Protocol Architect. Deliver precise technical specifications on RISEN nodes.",
        "content": "Protocol: Media Engineer. Synthesize sharp, futuristic, and impactful narratives.",
        "default": "Protocol: Core Intelligence. Deliver sharp, accurate, and markdown-optimized data."
    }

    messages = [
        {"role": "system", "content": RISEN_SYSTEM_PROMPT},
        {"role": "system", "content": mode_instruction.get(mode, mode_instruction["default"])},
        {"role": "system", "content": f"Neural_Context_Buffer:\n{context}"}
    ]

    try:
        messages.extend(history)
    except:
        pass

    messages.append({"role": "user", "content": user_message})

    try:
        stream = client.chat.completions.create(
            model=settings.MODEL,
            messages=messages,
            temperature=settings.TEMPERATURE,
            max_tokens=1000,
            stream=True
        )

        full_response = ""
        for chunk in stream:
            content = getattr(chunk.choices[0].delta, "content", None)
            if content:
                full_response += content
                yield content

        try:
            add_message(session_id, "user", user_message)
            add_message(session_id, "assistant", full_response)
        except:
            pass

    except Exception as e:
        print(f"🔥 NEURAL_STREAM_ERROR: {e}")
        yield "⚠️ Data stream instability detected."
