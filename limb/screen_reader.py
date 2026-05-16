from google import genai
from google.genai import types
from PIL import Image
import io

from config import GEMINI_API_KEY, LIMB_MODEL, MAX_RETRIES
from utils.logger import get_logger

logger = get_logger(__name__)

client = genai.Client(api_key=GEMINI_API_KEY)

SCREEN_READ_PROMPT = """
You are analyzing a screenshot from the mobile game "The Battle of Polytopia".

Extract the current game state and return it in this exact format:

TURN: <number> | STARS: <number> | TRIBE: <name>

MAP:
[row,col] YOUR <unit_type> HP:<hp>/<max_hp>
[row,col] ENEMY <unit_type> HP:<hp>/<max_hp>
[row,col] YOUR City Level:<n>
[row,col] NEUTRAL Village
[row,col] <terrain_type>

AVAILABLE ACTIONS:
- <action>

UI STATE:
- <anything visible: menus, popups, end turn button, etc.>

Only describe what you can clearly see. If unsure, write UNKNOWN.
Do not invent anything.
"""


def read_screen(screenshot_path: str) -> str:
    """
    Send a screenshot to Gemini and return the game state as structured text.
    """
    logger.info(f"Sending screenshot to Gemini: {screenshot_path}")

    # Open image and convert to bytes
    image = Image.open(screenshot_path)
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    image_bytes = buf.getvalue()

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=LIMB_MODEL,
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
                    SCREEN_READ_PROMPT,
                ],
            )
            state_text = response.text.strip()
            logger.info("Gemini successfully read the screen.")
            logger.debug(f"Game state:\n{state_text}")
            return state_text
        except Exception as e:
            logger.warning(f"Attempt {attempt} failed: {e}")
            if attempt == MAX_RETRIES:
                raise

    return ""
