from __future__ import annotations

from threading import Lock
from typing import ClassVar

from .config import Config


class ConfigFactory:
    """Provide a single shared :class:`Config` instance per process."""

    _lock: ClassVar[Lock] = Lock()
    _instance: ClassVar[Config | None] = None

    @classmethod
    def get_config(cls) -> Config:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = Config()
        return cls._instance
