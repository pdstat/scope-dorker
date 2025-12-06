from scopeminer import ProgramScope

class DorkResults:
    
    def __init__(self, prog_scope: ProgramScope, query: str, links: set[str]) -> None:
        self.program_scope = prog_scope
        self.query = query
        self.links = links
    
    def __str__(self) -> str:
        s = f"# Results for Program {self.program_scope.name} matching query '{self.query}'\n"
        for link in self.links:
            s += f"{link}\n"
        return s
    
    def get_program_name(self) -> str:
        return self.program_scope.get_name()
    
    def get_links(self) -> list[str]:
        return sorted(list(self.links))