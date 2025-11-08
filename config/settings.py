from __future__ import annotations
import json
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass(slots=True)
class AppConfig:
    libvirt_uri: str = "qemu:///system"
    log_level: str = "INFO"
    log_file: str = "libvirt_manager.log"
    theme: str = "light"
    window_width: int = 1000
    window_height: int = 700

    @classmethod
    def load(cls, config_path: Path) -> AppConfig:
        if config_path.exists():
            try:
                with open(config_path, encoding="utf-8") as f:
                    data = json.load(f)
                return cls(**data)
            except (json.JSONDecodeError, TypeError, OSError):
                pass
        return cls()

    def save(self, config_path: Path) -> None:
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(asdict(self), f, indent=2)
        except OSError:
            pass
