from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from services.router import route_request
from fastapi.responses import StreamingResponse
from services.stream_service import stream_ai_response
from services.rate_limit import rate_limit_check
from utils.auth import get_user_status
from services.usage_service import check_usage

router = APIRouter()

# ... (ChatRequest remains same)

# =========================
# 💬 CHAT (SAFE MODE)
# =========================
@router.post("/chat")
def chat(req: ChatRequest, user: dict = Depends(get_user_status)):
    try:
        session_id = req.session_id or user["id"]

        # ✅ Check Usage
        allowed, remaining = check_usage(user["id"], user["is_premium"], "prompt")
        if not allowed:
            return {
                "type": "text",
                "data": {
                    "content": "⚠️ **Neural Limit Reached.** Standard nodes are limited to 10 prompts per cycle. Upgrade to **Prime Elite** for limitless cognitive output."
                }
            }

        response = route_request(
            req.message,
            session_id=session_id,
            context=req.context,
            user=user
        )

        # Add usage info to metadata if possible
        if isinstance(response, dict) and "data" in response:
            response["metadata"] = {"remaining_prompts": remaining}

        return response

    except Exception as e:
        print("🔥 CHAT ERROR:", str(e))
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# 💬 STREAM (SAFE MODE)
# =========================
@router.post("/chat/stream")
def chat_stream(req: ChatRequest):

    session_id = req.session_id or "fallback"

    # 🔥 Rate limit (safe)
    #if not rate_limit_check(session_id):
    #    raise HTTPException(status_code=429, detail="Too many requests")

    def generator():
        try:
            for chunk in stream_ai_response(
                req.message,
                mode="default",
                session_id=session_id,
            ):
                yield chunk

        except Exception as e:
            print("🔥 STREAM ERROR:", str(e))
            yield "⚠️ Error occurred while streaming."

    return StreamingResponse(generator(), media_type="text/plain")