from openai import OpenAI
from core.config import settings

import base64
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter

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
            size = int(base.width * 0.12)
            logo = logo.resize((size, size))
            # Position at top right
            pos = (base.width - size - 60, 60)
            base.paste(logo, pos, logo)
    except Exception as e:
        print(f"[WARN] Logo overlay skipped: {e}")

    base.save(image_path)
    return image_path


def get_title(score):
    if score < 1000:
        return "NEURAL NOVICE"
    elif score < 5000:
        return "DATA SURFER"
    elif score < 10000:
        return "CORE TRADER"
    elif score < 25000:
        return "ELITE MINER"
    elif score < 50000:
        return "MATRIX ALPHA"
    else:
        return "ON-CHAIN DEITY"


def get_tier(rank):
    if rank <= 5:
        return "PRIME"
    elif rank <= 50:
        return "ELITE"
    return "CYBER"


def get_colors(tier):
    if tier == "PRIME":
        return (251, 191, 36) # Amber 400
    elif tier == "ELITE":
        return (168, 85, 247) # Purple 500
    return (46, 219, 255) # Risen Primary (Cyan)


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
    username = str(username or "UNKNOWN").upper()
    print(f"🎨 Generating standalone premium scorecard for {username} (Score: {score}, Rank: {rank})")

    # Create a pure aesthetic background (Deep Risen Space)
    base = Image.new("RGBA", (1024, 1024), (2, 7, 13, 255))
    overlay = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Styling Variables
    tier = get_tier(rank)
    accent_color = get_colors(tier)
    title = get_title(score)

    # Fonts
    f_path = get_font_path()
    try:
        if f_path:
            h1 = ImageFont.truetype(f_path, 100)
            h2 = ImageFont.truetype(f_path, 55)
            h3 = ImageFont.truetype(f_path, 32)
            stat_label = ImageFont.truetype(f_path, 28)
            stat_font = ImageFont.truetype(f_path, 110)
        else:
            h1 = h2 = h3 = stat_label = stat_font = ImageFont.load_default()
    except:
        h1 = h2 = h3 = stat_label = stat_font = ImageFont.load_default()

    # 1. Background Visuals (Grid & Glow)
    # Draw subtle tech grid
    grid_color = (*accent_color, 15)
    for i in range(0, 1024, 64):
        draw.line([i, 0, i, 1024], fill=grid_color, width=1)
        draw.line([0, i, 1024, i], fill=grid_color, width=1)

    # Central Radial Glow
    glow = Image.new("RGBA", (1024, 1024), (0,0,0,0))
    g_draw = ImageDraw.Draw(glow)
    for r in range(800, 0, -10):
        alpha = int((1 - r/800)**2 * 30)
        g_draw.ellipse([512-r, 512-r, 512+r, 512+r], fill=(*accent_color, alpha))
    base = Image.alpha_composite(base, glow)

    # 2. HUD Design Elements
    # Outer Framing
    draw.rectangle([40, 40, 984, 984], outline=(*accent_color, 60), width=2)

    # Sidebar Detail (Left)
    draw.rectangle([40, 40, 60, 984], fill=(*accent_color, 40))

    # Corner Geometric Accents
    # TL
    draw.polygon([(40, 40), (200, 40), (40, 200)], fill=(*accent_color, 100))
    # BR
    draw.polygon([(984, 984), (824, 984), (984, 824)], fill=(*accent_color, 100))

    # 3. Main Text Layout (Left Aligned)
    margin_x = 120

    # Brand Header
    draw.text((margin_x, 100), "RISEN RUSH", fill=(255,255,255), font=h1)
    draw.text((margin_x, 210), f"DECRYPTION PROTOCOL: {tier}", fill=accent_color, font=h3)

    # 4. Large Center Stats (Vertically Distributed)
    # Rank Section
    draw.text((margin_x, 320), "GLOBAL POSITION", fill=(255,255,255, 60), font=stat_label)
    draw.text((margin_x, 360), f"#{rank}", fill=accent_color, font=stat_font)

    # Score Section
    draw.text((margin_x, 520), "SYNCED COGNITION SCORE", fill=(255,255,255, 60), font=stat_label)
    draw.text((margin_x, 560), f"{score:,}", fill=(255,255,255), font=stat_font)

    # Identity Section (Bottom)
    draw.rectangle([margin_x, 740, 900, 742], fill=(*accent_color, 80))
    draw.text((margin_x, 780), "NEURAL IDENTITY", fill=(255,255,255, 60), font=stat_label)
    draw.text((margin_x, 820), f"@{username}", fill=(255,255,255), font=h2)

    # Cognitive Status (Floating Badge)
    status_text = f"[{title}]"
    s_w = draw.textlength(status_text, font=h3)
    draw.text((margin_x, 900), status_text, fill=accent_color, font=h3)

    # 5. Bottom Metadata (Technical Flair)
    timestamp = datetime.now().strftime("%Y.%m.%d / %H:%M:%S")
    draw.text((120, 950), f"BLOCK_TIME: {timestamp}", fill=(255,255,255, 40), font=h3)

    # 6. Final Composite
    combined = Image.alpha_composite(base, overlay)

    # Save
    filename = f"scorecard_{datetime.now().timestamp()}.png"
    path = os.path.join(GENERATED_DIR, filename)
    combined.save(path)

    # Add Logo (Positioned top right)
    add_logo_overlay(path)

    return path
