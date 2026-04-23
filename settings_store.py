import json
from pathlib import Path

from config import (
    DEFAULT_AUTO_SHUTDOWN_ENABLED,
    DEFAULT_GAME_PROCESS_NAMES,
    DEFAULT_LIMIT_MINUTES,
    DEFAULT_NETWORK_LIMIT_MB,
    SETTINGS_FILE,
)


class SettingsStore:
    def __init__(self, path=SETTINGS_FILE):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.ensure_exists()

    def ensure_exists(self):
        if not self.path.exists():
            self.save(self.default_settings())

    @staticmethod
    def default_settings():
        return {
            "game_process_names": sorted(DEFAULT_GAME_PROCESS_NAMES),
            "daily_limit_minutes": DEFAULT_LIMIT_MINUTES,
            "network_limit_mb": DEFAULT_NETWORK_LIMIT_MB,
            "auto_shutdown_enabled": DEFAULT_AUTO_SHUTDOWN_ENABLED,
        }

    def load(self):
        self.ensure_exists()
        with self.path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def save(self, data):
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    def add_game(self, game_name):
        settings = self.load()
        games = {name.lower(): name for name in settings["game_process_names"]}
        normalized_name = game_name.strip()
        if not normalized_name:
            raise ValueError("Game name cannot be empty")
        if normalized_name.lower() in games:
            raise ValueError("Game already exists")
        settings["game_process_names"].append(normalized_name)
        settings["game_process_names"] = sorted(settings["game_process_names"])
        self.save(settings)
        return settings

    def remove_game(self, game_name):
        settings = self.load()
        updated_games = [
            name
            for name in settings["game_process_names"]
            if name.lower() != game_name.lower()
        ]
        if len(updated_games) == len(settings["game_process_names"]):
            raise ValueError("Game not found")
        settings["game_process_names"] = updated_games
        self.save(settings)
        return settings

    def update_limits(
        self,
        daily_limit_minutes=None,
        network_limit_mb=None,
        auto_shutdown_enabled=None,
    ):
        settings = self.load()
        if daily_limit_minutes is not None:
            settings["daily_limit_minutes"] = daily_limit_minutes
        if network_limit_mb is not None:
            settings["network_limit_mb"] = network_limit_mb
        if auto_shutdown_enabled is not None:
            settings["auto_shutdown_enabled"] = auto_shutdown_enabled
        self.save(settings)
        return settings
