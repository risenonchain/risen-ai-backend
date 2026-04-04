from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.router import route_request
from fastapi.responses import StreamingResponse
from services.stream_service import stream_ai_response
from services.rate_limit import rate_limit_check

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    context: dict = {}


# =========================
# 💬 CHAT (SAFE MODE)
# =========================
@router.post("/chat")
def chat(req: ChatRequest):
    try:
        session_id = req.session_id or "fallback"

        # 🔥 Rate limit (safe)
        if not rate_limit_check(session_id):
            raise HTTPException(status_code=429, detail="Too many requests")

        response = route_request(
            req.message,
            session_id=session_id,
            context=req.context
        )

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
    if not rate_limit_check(session_id):
        raise HTTPException(status_code=429, detail="Too many requests")

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