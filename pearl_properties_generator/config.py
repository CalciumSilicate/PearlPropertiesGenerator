import json
import os
from typing import Any, Dict, Optional

from mcdreforged.api.all import PluginServerInterface


class Config:
    DEFAULT_CONFIG = {
        "pearl_x": -99.0625,
        "pearl_z": 0.0625,
        "player_y": 139.0,
        "rotation": 0,
        "max_tnt": 1820,
        "ground_y": 0.0,
        "max_tick": 1000,
        "max_results": 100,
    }

    ROTATION_NAMES = ["None", "CW_90", "CW_180", "CCW_90"]

    CONFIG_KEYS = list(DEFAULT_CONFIG.keys())
    CONFIG_ALIASES = {
        "px": "pearl_x",
        "pz": "pearl_z",
        "py": "player_y",
        "gy": "ground_y",
    }

    def __init__(self, server: PluginServerInterface):
        self.server = server
        self.config_path = os.path.join(
            server.get_data_folder(), "config.json"
        )
        self.data: Dict[str, Any] = {}
        self.load()

    def load(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.data = {}

        for key, default_value in self.DEFAULT_CONFIG.items():
            if key not in self.data:
                self.data[key] = default_value

        self.save()

    def save(self):
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def get(self, key: str) -> Any:
        real_key = self.CONFIG_ALIASES.get(key, key)
        return self.data.get(real_key, self.DEFAULT_CONFIG.get(real_key))

    def set(self, key: str, value: Any) -> bool:
        real_key = self.CONFIG_ALIASES.get(key, key)
        if real_key not in self.DEFAULT_CONFIG:
            return False

        expected_type = type(self.DEFAULT_CONFIG[real_key])
        try:
            if expected_type == int:
                self.data[real_key] = int(value)
            elif expected_type == float:
                self.data[real_key] = float(value)
            else:
                self.data[real_key] = value
        except (ValueError, TypeError):
            return False

        self.save()
        return True

    def reset(self):
        self.data = dict(self.DEFAULT_CONFIG)
        self.save()

    def get_rotation_name(self) -> str:
        return self.ROTATION_NAMES[self.data.get("rotation", 0)]

    @staticmethod
    def resolve_key(key: str) -> Optional[str]:
        if key in Config.DEFAULT_CONFIG:
            return key
        return Config.CONFIG_ALIASES.get(key)
