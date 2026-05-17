# ============================================================
# environment/tribes_bridge.py
# Runs Tribes as a subprocess and reads its actions
# ============================================================

import subprocess
import os
from utils.logger import get_logger

logger = get_logger(__name__)

TRIBES_DIR = os.path.join(os.path.dirname(__file__), "..", "tribes")
JAVA_CMD = ["java", "-cp", "out;lib/json.jar", "Play"]


def parse_action(line: str) -> dict | None:
    """
    Parse a raw ACTION: line from Tribes into a structured dict.

    Examples:
        "ACTION:MOVE by unit 2 to 3 : 4"
        "ACTION:RESEARCH_TECH by tribe 0 : ORGANIZATION"
        "ACTION:END_TURN by tribe 0"
        "ACTION:ATTACK by unit 5 to unit 2"
        "ACTION:SPAWN by city 3 : WARRIOR"
    """
    if not line.startswith("ACTION:"):
        return None

    content = line[len("ACTION:") :].strip()

    try:
        if content.startswith("MOVE"):
            # MOVE by unit X to Y : Z
            parts = content.split()
            unit = int(parts[3])
            to_x = int(parts[5])
            to_y = int(parts[7])
            return {"type": "MOVE", "unit": unit, "to_x": to_x, "to_y": to_y}

        elif content.startswith("RESEARCH_TECH"):
            # RESEARCH_TECH by tribe X : TECHNAME
            tech = content.split(":")[-1].strip()
            tribe = int(content.split()[3])
            return {"type": "RESEARCH_TECH", "tribe": tribe, "tech": tech}

        elif content.startswith("END_TURN"):
            # END_TURN by tribe X
            tribe = int(content.split()[-1])
            return {"type": "END_TURN", "tribe": tribe}

        elif content.startswith("ATTACK"):
            # ATTACK by unit X to unit Y
            parts = content.split()
            attacker = int(parts[3])
            defender = int(parts[6])
            return {"type": "ATTACK", "attacker": attacker, "defender": defender}

        elif content.startswith("SPAWN"):
            # SPAWN by city X : UNITTYPE
            city = int(content.split()[3])
            unit_type = content.split(":")[-1].strip()
            return {"type": "SPAWN", "city": city, "unit_type": unit_type}

        elif content.startswith("LEVEL_UP"):
            # LEVEL_UP by city X with bonus Y
            parts = content.split()
            city = int(parts[3])
            bonus = parts[-1]
            return {"type": "LEVEL_UP", "city": city, "bonus": bonus}

        elif content.startswith("RESOURCE_GATHERED"):
            # RESOURCE_GATHERED by city X : RESOURCE
            city = int(content.split()[3])
            resource = content.split(":")[-1].strip()
            return {"type": "RESOURCE_GATHERED", "city": city, "resource": resource}

        elif content.startswith("DECLARE_WAR"):
            # DECLARE_WAR by tribe X on tribe Y
            parts = content.split()
            attacker = int(parts[3])
            defender = int(parts[6])
            return {"type": "DECLARE_WAR", "attacker": attacker, "defender": defender}

        elif content.startswith("SEND_STARS"):
            # SEND_STARS by tribe X to: Y : Z stars
            parts = content.split()
            sender = int(parts[3])
            stars = int(parts[-2])
            return {"type": "SEND_STARS", "sender": sender, "stars": stars}

        else:
            # Unknown action type — still return something
            return {"type": "UNKNOWN", "raw": content}

    except Exception as e:
        logger.warning(f"Could not parse action line: '{line}' — {e}")
        return {"type": "UNKNOWN", "raw": content}


def run_tribes_and_parse() -> list[dict]:
    logger.info("Starting Tribes subprocess...")

    process = subprocess.Popen(
        JAVA_CMD,
        cwd=TRIBES_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    actions = []
    current_tribe = 0  # track whose turn it is

    for line in process.stdout:
        line = line.strip()
        if line:
            logger.debug(f"Tribes: {line}")

        action = parse_action(line)
        if action and action.get("type") != "UNKNOWN":
            # Track current tribe from END_TURN and tribe-based actions
            if "tribe" in action:
                current_tribe = action["tribe"]

            # Only keep actions during tribe 0's turn
            if current_tribe == 0:
                logger.info(f"Parsed action: {action}")
                actions.append(action)

            # After END_TURN switch to next tribe
            if action["type"] == "END_TURN":
                current_tribe = 1 - current_tribe  # toggles 0→1→0

    process.wait()
    logger.info(f"Tribes finished. Total actions parsed: {len(actions)}")
    return actions
