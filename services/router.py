import os
from openai import OpenAI
from core.config import settings
from services.chat_service import get_ai_response
from services.media_service import generate_avatar_from_text
from services.stream_service import stream_ai_response

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def quick_intent_check(message: str):
    msg = message.lower()

    if any(word in msg for word in ["risen", "rsn", "tokenomics", "roadmap"]):
        return "RISEN_KNOWLEDGE"

    if any(word in msg for word in ["defi", "blockchain", "crypto", "token", "wallet"]):
        return "CRYPTO_EDUCATION"

    if any(word in msg for word in ["buy", "sell", "market", "price", "trend"]):
        return "MARKET"

    if any(word in msg for word in ["predict", "will", "future", "forecast"]):
        return "PREDICTION"

    if any(word in msg for word in ["avatar", "image", "meme", "generate"]):
        return "MEDIA"

    return None


def classify_intent(message: str) -> str:
    prompt = f"""
    Classify the user request into one of these categories:

    RISEN_KNOWLEDGE
    CRYPTO_EDUCATION
    MARKET
    PREDICTION
    MEDIA
    GENERAL

    Message: "{message}"

    Only return the category name.
    """

    response = client.chat.completions.create(
        model=settings.MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content.strip()


def map_intent_to_mode(intent: str) -> str:
    return {
        "RISEN_KNOWLEDGE": "risen",
        "CRYPTO_EDUCATION": "education",
        "MARKET": "market",
        "PREDICTION": "market",
        "MEDIA": "content",
        "GENERAL": "default"
    }.get(intent, "default")


# 🔥 UPDATED
def route_request(message: str, session_id: str = "default", context: dict = {}):

    intent = quick_intent_check(message)

    if not intent:
        intent = classify_intent(message)

    mode = map_intent_to_mode(intent)

    print(f"🧠 Detected intent: {intent} | Mode: {mode}")

    if intent == "MEDIA":
        image_url = generate_avatar_from_text(message)
        return {
            "type": "image",
            "data": {
                "image_url": image_url
            }
        }

    return get_ai_response(
        message,
        mode=mode,
        session_id=session_id,
        context=context  # 🔥 NEW
    )