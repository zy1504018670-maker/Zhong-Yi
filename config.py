import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

PLAYTIME_CSV = Path(os.getenv("CHILD_MONITOR_PLAYTIME_CSV", BASE_DIR / "playtime.csv"))
SETTINGS_FILE = Path(os.getenv("CHILD_MONITOR_SETTINGS_FILE", BASE_DIR / "settings.json"))
TASKS_FILE = Path(os.getenv("CHILD_MONITOR_TASKS_FILE", BASE_DIR / "tasks.json"))

DEFAULT_GAME_PROCESS_NAMES = {
    "YiqiyooBox.exe",
    "RobloxPlayerBeta.exe",
    "FortniteClient-Win64-Shipping.exe",
    "csgo.exe",
    "hl2.exe",
    "Among Us.exe",
    "GenshinImpact.exe",
}

DEFAULT_LIMIT_MINUTES = 120
DEFAULT_NETWORK_LIMIT_MB = 500.0
DEFAULT_AUTO_SHUTDOWN_ENABLED = os.getenv(
    "CHILD_MONITOR_AUTO_SHUTDOWN_ENABLED",
    "false",
).lower() == "true"

SCAN_INTERVAL = int(os.getenv("CHILD_MONITOR_SCAN_INTERVAL", "5"))
SHUTDOWN_GRACE_SECONDS = int(os.getenv("CHILD_MONITOR_SHUTDOWN_GRACE_SECONDS", "60"))
