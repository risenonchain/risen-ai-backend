import os
from openai import OpenAI
from core.config import settings
from services.chat_service import get_ai_response
from services.media_service import generate_avatar_from_text
from services.usage_service import check_usage

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
    RISEN_KNOWLEDGE, CRYPTO_EDUCATION, MARKET, PREDICTION, MEDIA, GENERAL
    Message: "{message}"
    Only return the category name.
    """
    try:
        response = client.chat.completions.create(
            model=settings.MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("🔥 INTENT CLASSIFICATION ERROR:", str(e))
        return "GENERAL"

def map_intent_to_mode(intent: str) -> str:
    return {
        "RISEN_KNOWLEDGE": "risen",
        "CRYPTO_EDUCATION": "education",
        "MARKET": "market",
        "PREDICTION": "market",
        "MEDIA": "content",
        "GENERAL": "default"
    }.get(intent, "default")

def route_request(message: str, session_id: str = "default", context: dict = None, user: dict = None):
    if context is None: context = {}
    if user is None: user = {"id": "anonymous", "is_premium": False}

    try:
        intent = quick_intent_check(message)
        if not intent:
            intent = classify_intent(message)

        mode = map_intent_to_mode(intent)
        print(f"🧠 Detected intent: {intent} | Mode: {mode}")

        if intent == "MEDIA":
            # Check Image Usage
            allowed, remaining = check_usage(user["id"], user["is_premium"], "image")
            if not allowed:
                return {
                    "type": "text",
                    "data": {
                        "content": "⚠️ **Media Generation Limit Reached.** Standard nodes are limited to 1 image per cycle. Upgrade to **Prime Elite** for limitless creations."
                    }
                }

            image_url = generate_avatar_from_text(message)
            return {
                "type": "image",
                "data": {
                    "image_url": image_url,
                    "remaining": remaining
                }
            }

        return get_ai_response(
            message,
            mode=mode,
            session_id=session_id,
            context=context
        )

    except Exception as e:
        import traceback
        print("🔥 ROUTE REQUEST ERROR:", str(e))
        traceback.print_exc()
        return {
            "type": "text",
            "data": {
                "content": f"⚠️ Neural link interrupted. Cognitive synthesis failed. Details: {str(e)}"
            }
        }
