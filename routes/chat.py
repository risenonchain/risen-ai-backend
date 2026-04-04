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
# 💬 CHAT (NO AUTH TEMP)
# =========================
@router.post("/chat")
def chat(req: ChatRequest):
    session_id = req.session_id

    # 🔥 Optional rate limit (using session instead of user)
    if not rate_limit_check(session_id):
        raise HTTPException(status_code=429, detail="Too many requests")

    return route_request(
        req.message,
        session_id=session_id,
        context=req.context
    )


# =========================
# 💬 STREAM (NO AUTH TEMP)
# =========================
@router.post("/chat/stream")
def chat_stream(req: ChatRequest):
    session_id = req.session_id

    # 🔥 Optional rate limit
    if not rate_limit_check(session_id):
        raise HTTPException(status_code=429, detail="Too many requests")

    def generator():
        for chunk in stream_ai_response(
            req.message,
            mode="default",
            session_id=session_id,
        ):
            yield chunk

    return StreamingResponse(generator(), media_type="text/plain")