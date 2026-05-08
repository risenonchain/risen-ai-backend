from openai import OpenAI
from core.config import settings

import base64
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

client = OpenAI(api_key=settings.OPENAI_API_KEY)

GENERATED_DIR = "generated_images"
# Try multiple possible logo locations
LOGO_PATHS = [
    "assets/risen_logo.png",
    "../risen-website/public/logo.png",
    "public/logo.png"
]
# Try multiple font locations
FONT_PATHS = [
    "assets/fonts/orbitron.ttf",
    "../risen-website/public/fonts/orbitron.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    "C:/Windows/Fonts/arial.ttf" # Fallback for local windows dev
]

def get_logo_path():
    for p in LOGO_PATHS:
        if os.path.exists(p): return p
    return None

def get_font_path():
    for p in FONT_PATHS:
        if os.path.exists(p): return p
    return None

def add_logo_overlay(image_path):
    base = Image.open(image_path).convert("RGBA")

    try:
        logo_path = get_logo_path()
        if logo_path:
            logo = Image.open(logo_path).convert("RGBA")
            size = int(base.width * 0.2)
            logo = logo.resize((size, size))
            pos = (base.width - size - 20, base.height - size - 20)
            base.paste(logo, pos, logo)
    except Exception as e:
        print(f"[WARN] Logo overlay skipped: {e}")

    base.save(image_path)
    return image_path


def get_title(score):
    if score < 1000:
        return "Newbie"
    elif score < 5000:
        return "Explorer"
    elif score < 10000:
        return "Trader"
    elif score < 20000:
        return "Elite Miner"
    else:
        return "Alpha"


def get_tier(rank):
    if rank <= 10:
        return "GOLD"
    elif rank <= 100:
        return "SILVER"
    return "NEON"


def get_colors(tier):
    if tier == "GOLD":
        return (255, 215, 0)
    elif tier == "SILVER":
        return (192, 192, 192)
    return (0, 255, 200)


def generate_avatar_from_text(user_input: str):
    prompt = f"""
    Create a futuristic crypto avatar.

    Style:
    - cyberpunk
    - elite trader aesthetic
    - neon lighting
    - dark background

    User request:
    {user_input}
    """

    try:
        result = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            response_format="b64_json"
        )

        image_base64 = result.data[0].b64_json

        os.makedirs(GENERATED_DIR, exist_ok=True)

        filename = f"avatar_{datetime.now().timestamp()}.png"
        path = os.path.join(GENERATED_DIR, filename)

        with open(path, "wb") as f:
            f.write(base64.b64decode(image_base64))

        return f"/images/{filename}"
    except Exception as e:
        print(f"🔥 AVATAR GENERATION ERROR: {e}")
        return "/images/default-avatar.png"


# ==============================
# 🔹 SCORECARD
# ==============================
import requests
from io import BytesIO

def generate_scorecard(avatar_path, score, rank, username):
    print(f"🎨 Generating scorecard for {username} (Score: {score}, Rank: {rank})")
    print(f"🖼️ Avatar path: {avatar_path}")
    # Support avatar_path as URL or local path
    try:
        if str(avatar_path).startswith("http"):
            response = requests.get(avatar_path, timeout=10)
            response.raise_for_status()
            avatar_img = Image.open(BytesIO(response.content)).convert("RGBA")
        else:
            # Handle local paths or paths from static mount
            local_path = avatar_path
            if str(avatar_path).startswith("/images/"):
                local_path = os.path.join(GENERATED_DIR, avatar_path.replace("/images/", ""))
            elif str(avatar_path).startswith("images/"):
                 local_path = os.path.join(GENERATED_DIR, avatar_path.replace("images/", ""))

            if not os.path.exists(local_path):
                # Try prepending GENERATED_DIR if it's just a filename
                test_path = os.path.join(GENERATED_DIR, os.path.basename(avatar_path))
                if os.path.exists(test_path):
                    local_path = test_path
                else:
                    local_path = os.path.join(GENERATED_DIR, "default-avatar.png")

            if not os.path.exists(local_path):
                 print(f"⚠️ Local avatar not found at {local_path}, using blank background")
                 avatar_img = Image.new("RGBA", (1024, 1024), (10, 20, 30, 255))
            else:
                 avatar_img = Image.open(local_path).convert("RGBA")
    except Exception as e:
        print(f"[WARN] Avatar load failed ({avatar_path}): {e}, using fallback.")
        avatar_img = Image.new("RGBA", (1024, 1024), (10, 20, 30, 255))

    base = avatar_img.resize((1024, 1024))
    draw = ImageDraw.Draw(base)

    title = get_title(score)
    tier = get_tier(rank)
    color = get_colors(tier)

    try:
        f_path = get_font_path()
        if f_path:
            title_font = ImageFont.truetype(f_path, 70)
            text_font = ImageFont.truetype(f_path, 40)
        else:
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
    except Exception as e:
        print(f"[WARN] Font load error, using default: {e}")
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()

    # Header
    draw.text((50, 30), "RISEN RUSH ⚡", fill=color, font=title_font)

    # Username
    draw.text((50, 120), f"@{username}", fill=(255,255,255), font=text_font)

    # Rank / Score
    draw.text((50, 820), f"Rank: #{rank}", fill=color, font=text_font)
    draw.text((50, 880), f"Score: {score}", fill=color, font=text_font)

    # Title
    draw.text((50, 940), f"{title}", fill=color, font=text_font)

    filename = f"scorecard_{datetime.now().timestamp()}.png"
    path = os.path.join(GENERATED_DIR, filename)

    base.save(path)
    add_logo_overlay(path)

    return path