from pathlib import Path
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from services.media_service import generate_avatar_from_text, generate_scorecard
from utils.auth import get_user_status
from services.usage_service import check_usage

router = APIRouter()

class ScorecardRequest(BaseModel):
    avatar_path: str
    score: int
    rank: int
    username: str

@router.post("/generate-scorecard")
def generate_scorecard_api(req: ScorecardRequest, request: Request, user: dict = Depends(get_user_status)):
    if not user["is_premium"]:
        raise HTTPException(status_code=403, detail="Prime Protocol required for Scorecard generation")

    try:
        avatar_path = (req.avatar_path or "").strip()
        if not avatar_path:
            avatar_path = "/images/default-avatar.png"
        path = generate_scorecard(avatar_path, req.score, req.rank, req.username)
        filename = Path(path).name

        prefix = "/ai" if "/ai" in request.url.path else ""
        image_url = str(request.base_url).rstrip("/") + prefix + f"/download/scorecard/{filename}"

        return {"status": "success", "image_url": image_url}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Scorecard generation failed: {str(e)}")

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
        if avatar_path and score is not None and rank is not None and username:
            try:
                path = generate_scorecard(avatar_path, int(score), int(rank), username)
                if Path(path).name != filename:
                    Path(path).rename(file_path)
                return FileResponse(str(file_path), media_type="image/png", filename=filename)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Scorecard regeneration failed: {e}")
        raise HTTPException(status_code=404, detail="Scorecard not found")
    return FileResponse(str(file_path), media_type="image/png", filename=filename)

class MediaRequest(BaseModel):
    prompt: str

@router.post("/generate-avatar")
def generate_avatar(req: MediaRequest, request: Request, user: dict = Depends(get_user_status)):
    try:
        allowed, remaining = check_usage(user["id"], user["is_premium"], "image")
        if not allowed:
             return {
                "type": "error",
                "data": {
                    "content": "⚠️ **Media Generation Limit Reached.** Standard nodes are limited to 1 image per cycle. Upgrade to **Prime Elite** for limitless creations."
                }
            }

        image_path = generate_avatar_from_text(req.prompt)
        filename = Path(image_path).name
        image_url = str(request.base_url).rstrip("/") + f"/images/{filename}"
        return {
            "type": "image",
            "data": {
                "image_url": image_url,
                "remaining": remaining
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Avatar generation failed: {str(e)}")
