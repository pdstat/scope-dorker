class ProgramScope:
    
    def __init__(self, name: str, url_assets: set[str]) -> None:
        self._name = name
        self._url_assets = url_assets
   
    def get_name(self) -> str:
        return self._name
        
    def get_url_assets(self) -> list[str]:
        return sorted(list(self._url_assets))
    
    def add_url_asset(self, asset: str) -> None:
        self._url_assets.add(asset)