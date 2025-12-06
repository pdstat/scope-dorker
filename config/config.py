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
        search_count_path = config_dir / "search-count.json"

        if not config_path.exists():
            config_path.write_text(json.dumps(DEFAULT_CONFIG, indent=4), encoding="utf-8")

        if not search_count_path.exists():
            search_count_path.write_text(json.dumps(DEFAULT_SEARCH_COUNT, indent=4), encoding="utf-8")

        with config_path.open("r", encoding="utf-8") as f:
            self.config_data = json.load(f)

    def get_hackerone_config(self) -> dict[str, Any]:
        return self.config_data.get("apis", {}).get("h1", {})

    def get_google_config(self) -> dict[str, Any]:
        return self.config_data.get("apis", {}).get("google", {})

    def get_hackerone_credentials(self) -> tuple[str, str]:
        h1 = self.get_hackerone_config()
        return h1.get("username", ""), h1.get("api-key", "")
    
    def increment_search_count(self, increment: int = 1) -> None:
        user_home = Path.home()
        config_dir = user_home / ".config"
        search_count_path = config_dir / "search-count.json"

        with search_count_path.open("r", encoding="utf-8") as f:
            search_count_data = json.load(f)

        today_str = datetime.datetime.now().strftime(DATE_FORMAT)
        current_count = search_count_data.get(today_str, 0)
        search_count_data[today_str] = current_count + increment

        with search_count_path.open("w", encoding="utf-8") as f:
            json.dump(search_count_data, f, indent=4)
    
    def get_search_count(self) -> int:
        user_home = Path.home()
        config_dir = user_home / ".config"
        search_count_path = config_dir / "search-count.json"

        with search_count_path.open("r", encoding="utf-8") as f:
            search_count_data = json.load(f)

        today_str = datetime.datetime.now().strftime(DATE_FORMAT)
        return search_count_data.get(today_str, 0)

    