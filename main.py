print("🔥 RISEN AI NEW DEPLOY ACTIVE")
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import BackgroundTasks
from knowledge_base.retriever import reload_vector_store
from routes.chat import router as chat_router
from routes.media import router as media_router
from routes.session import router as session_router
from routes.stats import router as stats_router
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="RISEN AI",
    description="RISEN AI Intelligence Layer",
    version="1.0.0"
)

# ✅ CREATE IMAGE FOLDER
os.makedirs("generated_images", exist_ok=True)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://www.risenonchain.net",
        "https://risenonchain.net",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ ROUTES
app.include_router(chat_router, prefix="/ai")
app.include_router(media_router, prefix="/ai")
app.include_router(session_router, prefix="/ai")
app.include_router(stats_router, prefix="")

# Admin endpoint to reload RISEN knowledge base (POST /reload-kb)
@app.post("/reload-kb")
def reload_kb(background_tasks: BackgroundTasks):
    """
    Reload the RISEN knowledge base from .md files (admin/ops only).
    """
    background_tasks.add_task(reload_vector_store)
    return {"status": "reloading", "detail": "Knowledge base reload started."}

# ✅ STATIC FILES
app.mount("/images", StaticFiles(directory="generated_images"), name="images")


@app.get("/")
def root():
    return {"message": "RISEN AI is running"}