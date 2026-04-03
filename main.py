from fastapi import FastAPI
from routes.chat import router as chat_router
from routes.media import router as media_router
from fastapi.staticfiles import StaticFiles
from routes.session import router as session_router


app = FastAPI(
    title="RISEN AI",
    description="RISEN AI Intelligence Layer",
    version="1.0.0"
)

# Include routes
app.include_router(chat_router, prefix="/ai")
app.include_router(media_router, prefix="/ai")
app.mount("/images", StaticFiles(directory="generated_images"), name="images")
app.include_router(session_router, prefix="/ai")


@app.get("/")
def root():
    return {"message": "RISEN AI is running"}