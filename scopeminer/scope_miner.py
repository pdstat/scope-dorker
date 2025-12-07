from abc import ABC, abstractmethod

from .program_scope import ProgramScope

class ScopeMiner(ABC):
    @abstractmethod
    def get_program_scopes(self, authz: str, handle: str, include_oos: bool) -> ProgramScope:
        pass
    @abstractmethod
    def get_all_scopes(self, authz: str, include_oos: bool) -> list[ProgramScope]:
        pass