
from fastapi import APIRouter
from pydantic import BaseModel
from services.media_service import generate_avatar_from_text, generate_scorecard

router = APIRouter()

class ScorecardRequest(BaseModel):
    avatar_path: str
    score: int
    rank: int
    username: str


@router.post("/generate-scorecard")
def generate_scorecard_api(req: ScorecardRequest):
    path = generate_scorecard(req.avatar_path, req.score, req.rank, req.username)
    filename = path.split("\\")[-1]
    image_url = f"http://127.0.0.1:8000/images/{filename}"
    return {"status": "success", "image_url": image_url}


class MediaRequest(BaseModel):
    prompt: str


@router.post("/generate-avatar")
def generate_avatar(req: MediaRequest):
    image_path = generate_avatar_from_text(req.prompt)

    filename = image_path.split("\\")[-1]

    image_url = f"http://127.0.0.1:8000/images/{filename}"

    return {
        "status": "success",
        "image_url": image_url
    }