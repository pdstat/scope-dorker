import time
from collections import deque
from typing import Deque

from config import Config
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from scopeminer import ProgramScope

from .dork_result import DorkResults
from .scope_query_factory import ScopeQueryFactory

class GoogleDorker:
    def __init__(self, config: Config) -> None:
        self._config = config
        google_config = self._config.get_google_config()
        self._api_key = google_config.get("api-key", "")
        self._cse_id = google_config.get("cse-id", "")
        self._program_result_limit = google_config.get("program-result-limit", 100)
        self._max_results_limit = google_config.get("search-limit", 10000)
        self._max_backoff_attempts = 5
        self._base_backoff_seconds = 1.5
        self._request_window_seconds = 60
        self._request_window_limit = 100
        self._request_timestamps: Deque[float] = deque()

    def execute_dork(self, query: str, prog_scope: ProgramScope) -> DorkResults:
        try:
            service = build("customsearch", "v1", developerKey=self._api_key)
            all_results = set()
            
            dorks = ScopeQueryFactory.create_scope_querys(query, prog_scope)
            for dork in dorks:
                # Initial starting index is 1 (the first result)
                start_index = 1
                page_number = 1

                while True:
                    if len(all_results) >= self._program_result_limit or self._config.get_search_count() >= self._max_results_limit:
                        break

                    # Calculate how many results to request on this page
                    remaining_to_fetch = self._program_result_limit - len(all_results)
                    # Request up to the API's maximum (10) or the remaining amount
                    results_to_request = min(10, remaining_to_fetch)

                    result = self._execute_with_backoff(
                        service=service,
                        query=dork,
                        num=results_to_request,
                        start_index=start_index,
                    )

                    # 2. Process returned items
                    items = result.get("items", [])
                    if items:
                        before = len(all_results)
                        all_results.update(item.get('link') for item in items if item.get('link'))
                        fetched_links = len(all_results) - before
                        if fetched_links:
                            self._config.increment_search_count(fetched_links)
            
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
            print(f"Ensure your API Key {self._api_key} and CSE ID {self._cse_id} are correct and the API is enabled.")
            raise SystemExit()

    def _execute_with_backoff(self, service, query: str, num: int, start_index: int):
        attempt = 0
        while True:
            try:
                self._await_request_slot()
                return (
                    service.cse()
                    .list(q=query, cx=self._cse_id, num=num, start=start_index)
                    .execute()
                )
            except HttpError as exc:
                attempt += 1
                message = ""
                try:
                    error_payload = exc.error_details or []
                except AttributeError:
                    error_payload = []
                if error_payload:
                    message = str(error_payload[0].get("message", ""))

                allowed_message = "Quota exceeded for quota metric 'Queries' and limit 'Queries per minute per user'"
                should_retry = exc.resp.status == 429 and allowed_message in message

                if not should_retry or attempt >= self._max_backoff_attempts:
                    raise
                sleep_for = self._base_backoff_seconds * (2 ** (attempt - 1))
                time.sleep(sleep_for)

    def _await_request_slot(self) -> None:
        """Throttle requests to stay within 100 queries per minute."""
        while True:
            now = time.monotonic()
            while self._request_timestamps and now - self._request_timestamps[0] >= self._request_window_seconds:
                self._request_timestamps.popleft()

            if len(self._request_timestamps) < self._request_window_limit:
                self._request_timestamps.append(now)
                return

            oldest = self._request_timestamps[0]
            sleep_for = self._request_window_seconds - (now - oldest) + 0.01
            if sleep_for > 0:
                time.sleep(sleep_for)
