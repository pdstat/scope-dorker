from abc import ABC, abstractmethod

class ScopeMiner(ABC):
    @abstractmethod
    def get_program_scopes(self, authz: str, handle: str, include_oos: bool) -> list[str]:
        pass
    @abstractmethod
    def get_all_scopes(self, authz: str, include_oos: bool) -> list[str]:
        pass