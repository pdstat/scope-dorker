import argparse
import base64
import json
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
        help="The query portion of the dork to AND with the scoped site: clauses",
    )
    parser.add_argument(
        "-eos",
        "--exclude-out-of-scope",
        action="store_true",
        help="Exclude out-of-scope sites from the generated dorks",
    )
    parser.add_argument(
        "-p",
        "--programs",
        nargs="+",
        help="List of HackerOne program IDs to include in the dorking process",
    )
    parser.add_argument(
        "-os",
        "--output-scopes",
        help="Output the program scopes to a file",
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
                scopes = miner.get_program_scopes(
                    auth_header,
                    program_id,
                    include_oos=not args.exclude_out_of_scope,
                )
                program_scopes.append(scopes)
        else:
            program_scopes.extend(
                miner.get_all_scopes(
                    auth_header,
                    include_oos=not args.exclude_out_of_scope,
                )
            )
    
        if args.output_scopes:
            with open(args.output_scopes, "w") as f:
                # Write output_scopes as JSON to file
                json_scopes = [
                    {
                        "program": prog_scope.get_name(),
                        "url_assets": prog_scope.get_url_assets(),
                    }
                    for prog_scope in program_scopes
                ]
                json.dump(json_scopes, f, indent=4)
        else:
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

