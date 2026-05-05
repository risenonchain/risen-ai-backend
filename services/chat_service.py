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
    context: dict = None
):
    if context is None:
        context = {}

    # 🔥 Intelligent Context Retrieval
    try:
        context_data = retrieve_context(user_message)
    except:
        context_data = ""

    history = get_history(session_id)
    if not isinstance(history, list):
        history = []

    mode_instruction = {
        "education": "System Protocol: Deep educational breakdown. Use step-by-step logic, bold terminology, and summary conclusions.",
        "market": "System Protocol: Quantitative market analysis. Prioritize risk assessment, trend indicators, and structural insights.",
        "risen": "System Protocol: Ecosystem architectural expert. Provide high-fidelity technical data regarding RISEN protocols and roadmap.",
        "content": "System Protocol: High-impact content creation. Minimalist, punchy, and strategically engineered for viral reach.",
        "default": "System Protocol: General cognitive mode. Respond with clarity, precision, and architectural authority."
    }

    messages = [
        {"role": "system", "content": RISEN_SYSTEM_PROMPT},
        {"role": "system", "content": mode_instruction.get(mode, mode_instruction["default"])},
        {"role": "system", "content": f"Knowledge_Node_Context:\n{context_data}"}
    ]

    if context:
        messages.append({"role": "system", "content": f"Active_User_Context: {context}"})

    try:
        messages.extend(history)
    except:
        pass

    messages.append({"role": "user", "content": user_message})

    try:
        # Using more tokens for "Gemini" standard complexity
        response = client.chat.completions.create(
            model=settings.MODEL,
            messages=messages,
            temperature=settings.TEMPERATURE,
            max_tokens=800
        )

        reply = response.choices[0].message.content

    except Exception as e:
        print(f"🔥 OPENAI_ENGINE_ERROR: {e}")
        return "⚠️ Neural core communication failure. Protocol interrupted."

    try:
        add_message(session_id, "user", user_message)
        add_message(session_id, "assistant", reply)
    except:
        pass

    return {
        "type": "text",
        "data": {
            "content": reply
        }
    }
