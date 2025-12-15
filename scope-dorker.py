import argparse
import base64
import json
from config import Config, ConfigFactory
from dorking import GoogleDorker
from scopeminer import H1ScopeMiner, ProgramScope


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
    parser.add_argument(
        "-is",
        "--input-scopes",
        help="Input the program scopes from a file",
    )
    
    return parser.parse_args()


def load_program_scopes(
    args: argparse.Namespace,
    miner: H1ScopeMiner,
    auth_header: str,
) -> list[ProgramScope]:
    program_scopes: list[ProgramScope] = []

    if args.input_scopes:
        try:
            with open(args.input_scopes, "r", encoding="utf-8") as file_handle:
                json_data = json.load(file_handle)
        except OSError:
            raise SystemExit(f"Error reading input scopes from {args.input_scopes}")

        for prog_scope_data in json_data:
            program_scopes.append(ProgramScope.from_json_data(prog_scope_data))
        return program_scopes

    if args.programs:
        for program_id in args.programs:
            program_scopes.append(
                miner.get_program_scopes(
                    auth_header,
                    program_id,
                    include_oos=not args.exclude_out_of_scope,
                )
            )
    else:
        program_scopes.extend(
            miner.get_all_scopes(
                auth_header,
                include_oos=not args.exclude_out_of_scope,
            )
        )

    return program_scopes


def output_program_scopes(
    args: argparse.Namespace,
    program_scopes: list[ProgramScope],
) -> None:
    try:
        with open(args.output_scopes, "w", encoding="utf-8") as file_handle:
            json.dump([scope.to_json_dict() for scope in program_scopes], file_handle, indent=4)
    except OSError as exc:
        raise SystemExit(f"Error writing output scopes to {args.output_scopes}: {exc}")


def generate_dorks(
    args: argparse.Namespace,
    program_scopes: list[ProgramScope],
    dorker: GoogleDorker,
) -> None:
    if not args.query:
        raise SystemExit("Error: A query must be provided when dorking scopes.")

    dork_results = []
    for program_scope in program_scopes:
        results = dorker.execute_dork(args.query, program_scope)
        if results is not None:
            dork_results.append(results)

    for result in dork_results:
        print(result)


def main() -> None:
    args = parse_args()
    config = ConfigFactory.get_config()
    try:
        auth_header = _build_auth_header(config)
        miner = H1ScopeMiner()
        dorker = GoogleDorker(config)

        program_scopes = load_program_scopes(args, miner, auth_header)

        if args.output_scopes:
            output_program_scopes(args, program_scopes)
        else:
            generate_dorks(args, program_scopes, dorker)
    finally:
        config.write_search_count()


if __name__ == "__main__":
    main()

