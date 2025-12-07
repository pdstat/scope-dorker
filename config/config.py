import json
import datetime
from pathlib import Path
from typing import Any

DATE_FORMAT = "%Y%m%d"

DEFAULT_CONFIG: dict[str, Any] = {
    "apis": {
        "h1": {
            "api-key": "<insert-your-h1-api-key>",
            "username": "<insert-your-h1-username>",
        },
        "google": {
            "api-key": "<insert-your-google-api-key>",
            "cse-id": "<insert-your-google-cse-id>",
            "program-result-limit": 20,
            "search-limit": 1000,
        },
    }
}

DEFAULT_SEARCH_COUNT: dict[str, int] = {
    datetime.datetime.now().strftime(DATE_FORMAT): 0
}

class Config:
    """Configuration loader for scope-dorker."""

    def __init__(self) -> None:
        user_home = Path.home()
        config_dir = user_home / ".config/scope-dorker"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_path = config_dir / "config.json"

        if not config_path.exists():
            config_path.write_text(json.dumps(DEFAULT_CONFIG, indent=4), encoding="utf-8")
            # Exit the program with a message to the user
            raise SystemExit(f"Config file created at {config_path}. Please update it with your API keys.")

        self._search_count = self._read_search_count()
        with config_path.open("r", encoding="utf-8") as f:
            self._config_data = json.load(f)

    def _read_search_count(self) -> int:
        user_home = Path.home()
        config_dir = user_home / ".config/scope-dorker"
        search_count_path = config_dir / "search-count.json"

        if not search_count_path.exists():
            search_count_path.write_text(json.dumps(DEFAULT_SEARCH_COUNT, indent=4), encoding="utf-8")

        with search_count_path.open("r", encoding="utf-8") as f:
            try:
                search_count_data = json.load(f)
            except json.JSONDecodeError:
                search_count_path.write_text(json.dumps(DEFAULT_SEARCH_COUNT, indent=4), encoding="utf-8")
                search_count_data = dict(DEFAULT_SEARCH_COUNT)

        today_str = datetime.datetime.now().strftime(DATE_FORMAT)
        return search_count_data.get(today_str, 0)

    def get_hackerone_config(self) -> dict[str, Any]:
        return self._config_data.get("apis", {}).get("h1", {})

    def get_google_config(self) -> dict[str, Any]:
        return self._config_data.get("apis", {}).get("google", {})

    def get_hackerone_credentials(self) -> tuple[str, str]:
        h1 = self.get_hackerone_config()
        return h1.get("username", ""), h1.get("api-key", "")
    
    def write_search_count(self) -> None:
        user_home = Path.home()
        config_dir = user_home / ".config/scope-dorker"
        search_count_path = config_dir / "search-count.json"

        with search_count_path.open("r", encoding="utf-8") as f:
            search_count_data = json.load(f)

        today_str = datetime.datetime.now().strftime(DATE_FORMAT)
        search_count_data[today_str] = self._search_count

        with search_count_path.open("w", encoding="utf-8") as f:
            json.dump(search_count_data, f, indent=4)
    
    def increment_search_count(self, increment: int = 1) -> None:
        self._search_count += increment
    
    def get_search_count(self) -> int:
        return self._search_count

    