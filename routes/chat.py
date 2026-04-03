from fastapi import APIRouter, Depends
from pydantic import BaseModel
from risen_ai.services.router import route_request
from fastapi.responses import StreamingResponse
from risen_ai.services.stream_service import stream_ai_response
from risen_ai.utils.deps import get_current_ai_user

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"  # ✅ KEEP THIS (for safety)


@router.post("/chat")
def chat(
    req: ChatRequest,
    user=Depends(get_current_ai_user),
):
    # ✅ override session_id safely
    session_id = str(user["id"]) if user else req.session_id

    return route_request(req.message, session_id=session_id)


@router.post("/chat/stream")
def chat_stream(
    req: ChatRequest,
    user=Depends(get_current_ai_user),
):
    session_id = str(user["id"]) if user else req.session_id

    def generator():
        for chunk in stream_ai_response(
            req.message,
            mode="default",
            session_id=session_id,
        ):
            yield chunk

    return StreamingResponse(generator(), media_type="text/plain")