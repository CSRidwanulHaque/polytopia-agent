import subprocess
import time
import os
from config import ADB_PATH, EMULATOR_DEVICE_ID, SCREENSHOT_PATH
from utils.logger import get_logger

logger = get_logger(__name__)


def _adb(*args):
    """Run any adb command and return the output."""
    cmd = [ADB_PATH, "-s", EMULATOR_DEVICE_ID] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ADB error: {result.stderr.strip()}")
    return result.stdout.strip()


def take_screenshot(save_path: str = SCREENSHOT_PATH) -> str:
    """Take a screenshot of the emulator and save it locally."""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    logger.info("Taking screenshot...")
    _adb("shell", "screencap", "-p", "/sdcard/screen.png")
    _adb("pull", "/sdcard/screen.png", save_path)
    logger.info(f"Screenshot saved to {save_path}")
    return save_path


def tap(x: int, y: int, delay: float = 0.5):
    """Tap at pixel coordinates (x, y) on the emulator."""
    logger.info(f"Tapping ({x}, {y})")
    _adb("shell", "input", "tap", str(x), str(y))
    time.sleep(delay)


def swipe(x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300):
    """Swipe from one point to another."""
    logger.info(f"Swiping ({x1},{y1}) -> ({x2},{y2})")
    _adb("shell", "input", "swipe",
         str(x1), str(y1), str(x2), str(y2), str(duration_ms))


def long_press(x: int, y: int, duration_ms: int = 1000):
    """Long press at (x, y)."""
    logger.info(f"Long pressing ({x}, {y})")
    _adb("shell", "input", "swipe",
         str(x), str(y), str(x), str(y), str(duration_ms))