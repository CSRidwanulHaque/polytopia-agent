import os
from dotenv import load_dotenv

load_dotenv()

# --- API Keys ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- ADB Settings ---
ADB_HOST = "127.0.0.1"
ADB_PORT = 5555
EMULATOR_DEVICE_ID = "127.0.0.1:5555"
ADB_PATH = "C:/LDPlayer/LDPlayer9/adb.exe"

# --- Screen capture ---
SCREENSHOT_PATH = "temp/screenshot.png"

# --- Gemini Settings ---
LIMB_MODEL = "gemini-2.5-flash"  # the eye - reads screenshots
MAX_RETRIES = 3

# --- Logging ---
LOG_LEVEL = "INFO"
LOG_FILE = "logs/agent.log"
