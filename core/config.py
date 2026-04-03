import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # =========================
    # 🔐 CORE
    # =========================
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    MODEL = os.getenv("MODEL", "gpt-4o-mini")
    TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", 500))

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