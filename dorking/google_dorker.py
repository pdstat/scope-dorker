from config import Config
from googleapiclient.discovery import build
from scopeminer import ProgramScope
from .dork_result import DorkResults
from .scope_query_factory import ScopeQueryFactory

class GoogleDorker:
    def __init__(self):
        self.config = Config()
        google_config = self.config.get_google_config()
        self.api_key = google_config.get("api-key", "")
        self.cse_id = google_config.get("cse-id", "")
        self.program_result_limit = google_config.get("program-result-limit", 100)
        self.max_results_limit = google_config.get("search-limit", 10000)

    def execute_dork(self, query: str, prog_scope: ProgramScope) -> DorkResults:
        try:
            service = build("customsearch", "v1", developerKey=self.api_key)
            all_results = set()
            
            dorks = ScopeQueryFactory.create_scope_querys(query, prog_scope)
            for dork in dorks:
                # Initial starting index is 1 (the first result)
                start_index = 1
                page_number = 1

                while True:
                    if len(all_results) >= self.program_result_limit or self.config.get_search_count() >= self.max_results_limit:
                        break

                    # Calculate how many results to request on this page
                    remaining_to_fetch = self.program_result_limit - len(all_results)
                    # Request up to the API's maximum (10) or the remaining amount
                    results_to_request = min(10, remaining_to_fetch)

                    result = service.cse().list(
                        q=dork,
                        cx=self.cse_id,
                        num=results_to_request, # Use the calculated number of results
                        start=start_index
                    ).execute()
                    self.config.increment_search_count()

                    # 2. Process returned items
                    if 'items' in result:
                        # Add only the fetched items (which should be <= results_to_request)
                        all_results.update(item.get('link') for item in result['items'])
            
                    # 3. Check for the 'nextPage' indicator and update start index
                    if 'queries' in result and 'nextPage' in result['queries']:
                        next_page_info = result['queries']['nextPage'][0]
                        start_index = next_page_info['startIndex']
                        page_number += 1
                    else:
                        # 'nextPage' is absent, meaning we have reached the end of the results
                        break
                
                # for _, item in enumerate(all_results):
                #     all_results.add(item.get('link'))
            return DorkResults(prog_scope, query, all_results) if all_results else None
        except Exception as e:
            print(f"❌ An error occurred: {e}")
            print(f"Ensure your API Key {self.api_key} and CSE ID {self.cse_id} are correct and the API is enabled.")
