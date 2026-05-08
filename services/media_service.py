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
            size = int(base.width * 0.15)
            logo = logo.resize((size, size))
            # Position at top right with some flare logic
            pos = (base.width - size - 80, 80)

            # Glow behind logo
            glow_size = int(size * 1.5)
            glow = Image.new("RGBA", (glow_size, glow_size), (0,0,0,0))
            g_draw = ImageDraw.Draw(glow)
            for r in range(glow_size//2, 0, -2):
                alpha = int((1 - (r / (glow_size//2)))**2 * 100)
                g_draw.ellipse([glow_size//2-r, glow_size//2-r, glow_size//2+r, glow_size//2+r], fill=(46, 219, 255, alpha))

            base.paste(glow, (pos[0] + size//2 - glow_size//2, pos[1] + size//2 - glow_size//2), glow)
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
# 🔹 SCORECARD (PREMIUM V2)
# ==============================
import requests
from io import BytesIO

def generate_scorecard(avatar_path, score, rank, username):
    username = str(username or "UNKNOWN").upper()
    print(f"🎨 Generating ULTRA-PREMIUM scorecard for {username} (Score: {score}, Rank: {rank})")

    # 1. Base Canvas - Deep Futuristic Black/Blue
    base = Image.new("RGBA", (1024, 1024), (2, 5, 10, 255))
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
            h1 = ImageFont.truetype(f_path, 110)
            h2 = ImageFont.truetype(f_path, 60)
            h3 = ImageFont.truetype(f_path, 36)
            stat_label = ImageFont.truetype(f_path, 30)
            stat_font = ImageFont.truetype(f_path, 130)
            meta_font = ImageFont.truetype(f_path, 24)
        else:
            h1 = h2 = h3 = stat_label = stat_font = meta_font = ImageFont.load_default()
    except:
        h1 = h2 = h3 = stat_label = stat_font = meta_font = ImageFont.load_default()

    # 2. BACKGROUND HUD ELEMENTS (The "Premium" touches)
    # A. Subtle Linear Grid
    grid_color = (*accent_color, 20)
    for i in range(0, 1024, 40):
        draw.line([i, 0, i, 1024], fill=grid_color, width=1)
        draw.line([0, i, 1024, i], fill=grid_color, width=1)

    # B. RADAR SCANNERS (Right Side)
    radar_center = (800, 450)
    for r in range(50, 400, 80):
        draw.ellipse([radar_center[0]-r, radar_center[1]-r, radar_center[0]+r, radar_center[1]+r], outline=(*accent_color, 40), width=1)
    # Crosshairs for Radar
    draw.line([radar_center[0]-420, radar_center[1], radar_center[0]+420, radar_center[1]], fill=(*accent_color, 25), width=1)
    draw.line([radar_center[0], radar_center[1]-420, radar_center[0], radar_center[1]+420], fill=(*accent_color, 25), width=1)

    # C. Dynamic Radial Glow (Left/Center biased)
    glow = Image.new("RGBA", (1024, 1024), (0,0,0,0))
    g_draw = ImageDraw.Draw(glow)
    for r in range(900, 0, -15):
        alpha = int((1 - r/900)**3 * 50)
        # Shift glow slightly left to balance the radar on right
        g_draw.ellipse([200-r, 512-r, 200+r, 512+r], fill=(*accent_color, alpha))
    base = Image.alpha_composite(base, glow)

    # 3. METALLIC HUD FRAME
    padding = 30
    # Outer double line
    draw.rectangle([padding, padding, 1024-padding, 1024-padding], outline=(*accent_color, 120), width=3)
    draw.rectangle([padding+10, padding+10, 1024-padding-10, 1024-padding-10], outline=(*accent_color, 40), width=1)

    # PREMIUM CORNER PLATES (Gold/Tier style)
    # Top Left Plate
    plate_size = 180
    draw.polygon([
        (padding, padding),
        (padding+plate_size, padding),
        (padding+plate_size-40, padding+40),
        (padding+40, padding+plate_size-40),
        (padding, padding+plate_size)
    ], fill=(*accent_color, 180))

    # Bottom Right Plate
    draw.polygon([
        (1024-padding, 1024-padding),
        (1024-padding-plate_size, 1024-padding),
        (1024-padding-plate_size+40, 1024-padding-40),
        (1024-padding-40, 1024-padding-plate_size+40),
        (1024-padding, 1024-padding-plate_size)
    ], fill=(*accent_color, 180))

    # 4. TYPOGRAPHY & LAYOUT
    margin_left = 110

    # A. BRAND HEADER (Beveled Effect Simulation)
    # Draw dark shadow
    draw.text((margin_left+4, 94), "RISEN RUSH", fill=(0,0,0,150), font=h1)
    # Main White Text
    draw.text((margin_left, 90), "RISEN RUSH", fill=(255,255,255), font=h1)

    draw.text((margin_left, 215), f"DECRYPTION PROTOCOL: {tier}", fill=accent_color, font=h3)

    # B. RANK DISPLAY
    draw.text((margin_left, 330), "GLOBAL POSITION", fill=(255,255,255, 90), font=stat_label)
    # Large Number with Glow-like feel (multiple offsets)
    rank_val = f"#{rank}"
    draw.text((margin_left+3, 373), rank_val, fill=(0,0,0,100), font=stat_font)
    draw.text((margin_left, 370), rank_val, fill=accent_color, font=stat_font)

    # C. SCORE DISPLAY
    draw.text((margin_left, 530), "SYNCED COGNITION SCORE", fill=(255,255,255, 90), font=stat_label)
    score_val = f"{score:,}"
    draw.text((margin_left+3, 573), score_val, fill=(0,0,0,100), font=stat_font)
    draw.text((margin_left, 570), score_val, fill=(255,255,255), font=stat_font)

    # D. IDENTITY BLOCK
    # Separator Line
    draw.line([margin_left, 740, 900, 740], fill=(*accent_color, 150), width=2)
    draw.text((margin_left, 775), "NEURAL IDENTITY", fill=(255,255,255, 90), font=stat_label)
    draw.text((margin_left, 815), f"@{username}", fill=(255,255,255), font=h2)

    # Status Badge (Premium Gold/Tier Background)
    status_w = draw.textlength(f" {title} ", font=h3)
    draw.rectangle([margin_left, 900, margin_left + status_w + 10, 945], fill=(*accent_color, 40), outline=accent_color, width=1)
    draw.text((margin_left + 5, 905), title, fill=accent_color, font=h3)

    # E. BLOCK TIME (Technical Metadata)
    timestamp = datetime.now().strftime("%Y.%m.%d / %H:%M:%S")
    draw.text((margin_left, 960), "BLOCK_TIME", fill=(255,255,255, 60), font=meta_font)
    draw.text((margin_left, 985), timestamp, fill=(255,255,255, 30), font=meta_font)

    # 5. FINAL COMPOSITE & SAVE
    combined = Image.alpha_composite(base, overlay)

    filename = f"scorecard_{datetime.now().timestamp()}.png"
    path = os.path.join(GENERATED_DIR, filename)
    combined.save(path)

    # 6. ADD LOGO (V2 with Glow)
    add_logo_overlay(path)

    return path
