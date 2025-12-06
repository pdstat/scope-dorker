import requests
from requests.adapters import HTTPAdapter, Retry

from .scope_miner import ScopeMiner
from .program_scope import ProgramScope

PROGRAMS_ENPOINT = "https://api.hackerone.com/v1/hackers/programs"
PROGRAMS_API_URL = f"{PROGRAMS_ENPOINT}?page%5Bsize%5D=100"

class H1ScopeMiner(ScopeMiner):
    def __normalise_domain(self, domain: str) -> str:
        domain = domain.strip()
        if not domain:
            return ""

        candidate = domain
        if "://" in candidate:
            candidate = candidate.split("://", 1)[1]
        if "/" in candidate:
            candidate = candidate.split("/", 1)[0]
        if "@" in candidate:
            candidate = candidate.split("@", 1)[1]
        if ":" in candidate:
            candidate = candidate.split(":", 1)[0]

        candidate = candidate.rstrip(".").lower()
        if candidate.startswith("*."):
            return f".{candidate[2:]}"

        return candidate


    def __get_program_scopes(self, authz: str, handle: str, include_oos: bool) -> ProgramScope:
        program_scopes = set()
        current_url = f"https://api.hackerone.com/v1/hackers/programs/{handle}/structured_scopes?page%5Bnumber%5D=1&page%5Bsize%5D=100"
        s = requests.Session()
        retries = Retry(total=3, backoff_factor=2)
        s.mount("https://", HTTPAdapter(max_retries=retries))
        while True:
            res = s.get(current_url, headers={"Authorization": f"Basic {authz}"})

            if res.status_code == 401:
                raise SystemExit(f"Failed to get scopes for program check API keys")

            data = res.json()
            scopes = data.get("data", [])
            for scope in scopes:
                attributes = scope.get("attributes", {})
                if "asset_type" in attributes and "URL" == attributes["asset_type"]:
                    asset_identifier = attributes.get("asset_identifier", "")
                    normalised_domain = self.__normalise_domain(asset_identifier)
                    if include_oos:
                        program_scopes.add(normalised_domain)
                    elif "eligible_for_bounty" in attributes and attributes["eligible_for_bounty"]:
                        program_scopes.add(normalised_domain)
            links = data.get("links", {})
            current_url = links.get("next")
            if not current_url:
                break

        return ProgramScope(name=handle, url_assets=program_scopes)

    def __get_program_handles(self, authz: str) -> list[str]:
        handles = []
        current_url = PROGRAMS_API_URL
        while True:
            res = requests.get(current_url, headers={"Authorization": f"Basic {authz}"})

            if res.status_code != 200:
                raise SystemExit(f"Failed to get programs: {res.status_code} {res.text}")
        
            data = res.json()
            programs = data.get("data", [])
            for program in programs:
                attributes = program.get("attributes", {})
                if "submission_state" in attributes and attributes["submission_state"] == "open":
                    if "offers_bounties" in attributes and attributes["offers_bounties"]:
                        handles.append(attributes.get("handle", ""))
        
            links = data.get("links", {})
            current_url = links.get("next")
            if not current_url:
                break

        return handles

    def get_program_scopes(self, authz: str, handle: str, include_oos: bool) -> ProgramScope:
        return self.__get_program_scopes(authz, handle, include_oos)

    def get_all_scopes(self, authz: str, include_oos: bool) -> list[ProgramScope]:
        all_scopes = list()
        program_handles = self.__get_program_handles(authz)
        for handle in program_handles:
            program_scopes = self.__get_program_scopes(authz, handle, include_oos)
            all_scopes.append(program_scopes)
        return all_scopes
    