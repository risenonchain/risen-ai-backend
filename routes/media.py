
from pathlib import Path
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from services.media_service import generate_avatar_from_text, generate_scorecard

router = APIRouter()

class ScorecardRequest(BaseModel):
    avatar_path: str
    score: int
    rank: int
    username: str

@router.post("/generate-scorecard")
def generate_scorecard_api(req: ScorecardRequest, request: Request):
    try:
        avatar_path = (req.avatar_path or "").strip()
        if not avatar_path:
            avatar_path = "/images/default-avatar.png"
        path = generate_scorecard(avatar_path, req.score, req.rank, req.username)
        filename = Path(path).name
        image_url = str(request.base_url).rstrip("/") + f"/images/{filename}"
        return {"status": "success", "image_url": image_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scorecard generation failed: {str(e)}")

class MediaRequest(BaseModel):
    prompt: str

@router.post("/generate-avatar")
def generate_avatar(req: MediaRequest, request: Request):
    try:
        image_path = generate_avatar_from_text(req.prompt)
        filename = Path(image_path).name
        image_url = str(request.base_url).rstrip("/") + f"/images/{filename}"
        return {"status": "success", "image_url": image_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Avatar generation failed: {str(e)}")