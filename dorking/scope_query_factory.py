from scopeminer import ProgramScope

class ScopeQueryFactory:
    """Factory to create scope query strings based on the supplied ProgramScope."""

    # Conservative limits (you can tune these)
    MAX_QUERY_LENGTH = 1800          # characters (well below ~2k URL limit)
    MAX_SITE_OPERATORS = 25          # avoid too many site: operators per query

    @staticmethod
    def _build_dork(assets: list[str], query: str) -> str:
        """
        Build a single Google dork for the given list of assets and query.
        Example: (site:asset1 OR site:asset2) AND inurl:/content
        """
        assets_clause = " OR ".join(f"site:{asset}" for asset in assets)
        # Wrap the sites clause in parentheses, then AND with the query
        return f"({assets_clause}) AND {query.strip()}"

    @classmethod
    def create_scope_querys(cls, query: str, prog_scope: ProgramScope) -> list[str]:
        """
        Create a list of Google dork strings for the given ProgramScope and query.

        - Splits the ProgramScope.url_assets into groups.
        - Each group is turned into one query of the form:
          (site:asset1 OR site:asset2 OR ...) AND <query>
        - Respects both a max query length and a max number of site: operators.
        """
        assets = prog_scope.get_url_assets()  # sorted list[str]
        if not assets:
            return []

        dorks: list[str] = []
        current_group: list[str] = []

        for asset in assets:
            # Try adding this asset to the current group
            tentative_group = current_group + [asset]
            tentative_dork = cls._build_dork(tentative_group, query)

            # If adding this asset exceeds limits, finalize the current group and start a new one
            if (
                len(tentative_dork) > cls.MAX_QUERY_LENGTH or
                len(tentative_group) > cls.MAX_SITE_OPERATORS
            ):
                if current_group:
                    dorks.append(cls._build_dork(current_group, query))
                # Start a new group with just this asset
                current_group = [asset]
            else:
                # Safe to add asset to current group
                current_group = tentative_group

        # Flush any remaining group
        if current_group:
            dorks.append(cls._build_dork(current_group, query))

        return dorks