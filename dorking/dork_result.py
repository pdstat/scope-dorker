from scopeminer import ProgramScope

class DorkResults:
    
    def __init__(self, prog_scope: ProgramScope, query: str, links: set[str]) -> None:
        self._program_scope = prog_scope
        self._query = query
        self._links = links
    
    def __str__(self) -> str:
        s = f"# Results for Program {self._program_scope._name} matching query '{self._query}'\n"
        for link in self._links:
            s += f"{link}\n"
        return s
    
    def get_program_name(self) -> str:
        return self._program_scope.get_name()
    
    def get_links(self) -> list[str]:
        return sorted(list(self._links))