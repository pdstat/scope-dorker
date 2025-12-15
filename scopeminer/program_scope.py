from __future__ import annotations

class ProgramScope:
    
    def __init__(self, platform: str, name: str, url_assets: set[str]) -> None:
        self._platform = platform
        self._name = name
        self._url_assets = url_assets
   
    def get_name(self) -> str:
        return self._name
        
    def get_url_assets(self) -> list[str]:
        return sorted(list(self._url_assets))
    
    def get_platform(self) -> str:
        return self._platform
    
    def add_url_asset(self, asset: str) -> None:
        self._url_assets.add(asset)
    
    def to_json_dict(self) -> dict:
        return {
            "platform": self._platform,
            "name": self._name,
            "url_assets": sorted(list(self._url_assets)),
        }
        
    @classmethod
    def from_json_data(cls, json_data: dict) -> ProgramScope:
        """
        Creates a ProgramScope instance from a JSON dictionary.
        
        Note: The 'url_assets' from JSON will be a list, but we convert it to a set
              before passing it to __init__.
        """
        # Dictionary keys must match the parameter names in __init__
        platform = json_data.get("platform")
        name = json_data.get("name")
        
        # Ensure url_assets is present and convert list (from JSON) to a set (for __init__)
        url_assets_list = json_data.get("url_assets", [])
        url_assets_set = set(url_assets_list)
        
        if platform is None or name is None:
             raise ValueError("JSON data is missing required fields: 'platform' or 'name'")
             
        # Create and return the new object instance
        return cls(platform=platform, name=name, url_assets=url_assets_set)