import argparse
import base64
from config import Config, ConfigFactory
from dorking import GoogleDorker
from scopeminer import H1ScopeMiner


def _build_auth_header(config: Config) -> str:
    username, api_key = config.get_hackerone_credentials()
    credentials = f"{username}:{api_key}"
    return base64.b64encode(credentials.encode("utf-8")).decode("ascii")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Google dorks from HackerOne program scopes"
    )
    parser.add_argument(
        "-q",
        "--query",
        required=True,
        help="The query portion of the dork to AND with the scoped site: clauses",
    )
    parser.add_argument(
        "-oos",
        "--out-of-scope",
        default=True,
        help="Include out-of-scope sites in the generated dorks",
    )
    parser.add_argument(
        "-p",
        "--programs",
        nargs="+",
        help="List of HackerOne program IDs to include in the dorking process",
    )
    
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = ConfigFactory.get_config()
    try:
        auth_header = _build_auth_header(config)
        miner = H1ScopeMiner()
        dorker = GoogleDorker(config)

        dork_results = list()
        program_scopes = list()
        if args.programs:
            for program_id in args.programs:
                scopes = miner.get_program_scopes(auth_header, program_id, include_oos=args.out_of_scope)
                program_scopes.append(scopes)
        else:
            program_scopes.append(miner.get_all_scopes(auth_header, include_oos=args.out_of_scope))
    
        for program_scope in program_scopes:
            results = dorker.execute_dork(args.query, program_scope)
            if results is not None:
                dork_results.append(results)

        for result in dork_results:
            print(result)
    finally:
        config.write_search_count()


if __name__ == "__main__":
    main()

