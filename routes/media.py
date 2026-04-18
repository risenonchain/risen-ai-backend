

from pathlib import Path
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
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
        image_url = str(request.base_url).rstrip("/") + f"/download/scorecard/{filename}"
        return {"status": "success", "image_url": image_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scorecard generation failed: {str(e)}")

# Download endpoint for scorecard images

# On-demand scorecard generation and download
@router.get("/download/scorecard/{filename}")
def download_scorecard(
    filename: str,
    avatar_path: str = None,
    score: int = None,
    rank: int = None,
    username: str = None
):
    file_path = Path("generated_images") / filename
    if not file_path.exists():
        # Try to regenerate if all params are provided
        if avatar_path and score is not None and rank is not None and username:
            from services.media_service import generate_scorecard
            try:
                path = generate_scorecard(avatar_path, int(score), int(rank), username)
                if Path(path).name != filename:
                    # Rename to match requested filename
                    Path(path).rename(file_path)
                return FileResponse(str(file_path), media_type="image/png", filename=filename)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Scorecard regeneration failed: {e}")
        raise HTTPException(status_code=404, detail="Scorecard not found and cannot be regenerated (missing params)")
    return FileResponse(str(file_path), media_type="image/png", filename=filename)

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