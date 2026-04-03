from fastapi import APIRouter
import uuid

router = APIRouter()


@router.get("/session/init")
def init_session():
    return {
        "session_id": str(uuid.uuid4())
    }