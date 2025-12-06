class ProgramScope:
    
    def __init__(self, name: str, url_assets: set[str]) -> None:
        self.name = name
        self.url_assets = url_assets
   
    def get_name(self) -> str:
        return self.name
        
    def get_url_assets(self) -> list[str]:
        return sorted(list(self.url_assets))
    
    def add_url_asset(self, asset: str) -> None:
        self.url_assets.add(asset)