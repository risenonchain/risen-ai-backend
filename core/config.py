import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # =========================
    # 🔐 CORE
    # =========================
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    VECTOR_DB_PATH: str = "knowledge_base/db" 

    MODEL = os.getenv("MODEL", "gpt-4o-mini")
    TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", 500))

    # Verification
    RUSH_API_URL = os.getenv("NEXT_PUBLIC_RUSH_API_URL", "https://risen-rush-backend.onrender.com")

    # =========================
    # 🔴 REDIS (UPSTASH)
    # =========================
    REDIS_URL = os.getenv("REDIS_URL")
    REDIS_TOKEN = os.getenv("REDIS_TOKEN")

    def validate(self):
        if not self.OPENAI_API_KEY:
            raise ValueError("❌ OPENAI_API_KEY missing")

        # 🔥 TEMPORARY: allow Redis optional (for local dev)
        if not self.REDIS_URL or not self.REDIS_TOKEN:
            print("⚠️ Redis not configured — falling back to in-memory")


settings = Settings()
settings.validate()