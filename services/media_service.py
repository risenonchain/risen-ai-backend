from openai import OpenAI
from core.config import settings

import base64
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

client = OpenAI(api_key=settings.OPENAI_API_KEY)

GENERATED_DIR = "generated_images"
LOGO_PATH = "assets/risen_logo.png"
FONT_PATH = "assets/fonts/orbitron.ttf"


# ==============================
# 🔹 UTILS
# ==============================
def save_base64_image(image_base64, prefix="img"):
    os.makedirs(GENERATED_DIR, exist_ok=True)

    filename = f"{prefix}_{datetime.now().timestamp()}.png"
    path = os.path.join(GENERATED_DIR, filename)

    with open(path, "wb") as f:
        f.write(base64.b64decode(image_base64))

    return path


def add_logo_overlay(image_path):
    base = Image.open(image_path).convert("RGBA")

    if os.path.exists(LOGO_PATH):
        logo = Image.open(LOGO_PATH).convert("RGBA")
        size = int(base.width * 0.2)
        logo = logo.resize((size, size))

        pos = (base.width - size - 20, base.height - size - 20)
        base.paste(logo, pos, logo)

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

    from openai import OpenAI
    from risen_ai.core.config import settings
    import base64
    import os
    from datetime import datetime

    client = OpenAI(api_key=settings.OPENAI_API_KEY)

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

    result = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024"
    )

    image_base64 = result.data[0].b64_json

    os.makedirs("generated_images", exist_ok=True)

    filename = f"avatar_{datetime.now().timestamp()}.png"
    path = os.path.join("generated_images", filename)

    with open(path, "wb") as f:
        f.write(base64.b64decode(image_base64))

    return path


# ==============================
# 🔹 SCORECARD
# ==============================
def generate_scorecard(avatar_path, score, rank, username):

    base = Image.open(avatar_path).convert("RGBA").resize((1024, 1024))
    draw = ImageDraw.Draw(base)

    title = get_title(score)
    tier = get_tier(rank)
    color = get_colors(tier)

    try:
        title_font = ImageFont.truetype(FONT_PATH, 70)
        text_font = ImageFont.truetype(FONT_PATH, 40)
    except:
        title_font = None
        text_font = None

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