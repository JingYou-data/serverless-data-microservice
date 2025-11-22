"""
Robust API client with retry and backoff mechanisms
"""

import time
import requests

from src.utils.retry import calculate_backoff


class RobustAPIClient:
    """
    Robust API client with exponential backoff and retry

    Features:
        - Exponential backoff with jitter
        - Rate limit handling
        - Detailed error logging
    """

    def __init__(self, base_url, token, stats, max_retries=5,
                 initial_backoff=1, request_timeout=30):
        """
        Initialize API client

        Args:
            base_url: API base URL
            token: Authentication token
            stats: IngestionStats instance for tracking
            max_retries: Maximum retry attempts
            initial_backoff: Initial backoff time in seconds
            request_timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.token = token
        self.stats = stats
        self.max_retries = max_retries
        self.initial_backoff = initial_backoff
        self.request_timeout = request_timeout

        # Initialize session with auth headers
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        })

    def fetch_page_with_retry(self, endpoint, page, limit):
        """
        Fetch a single page of data with retry mechanism

        Args:
            endpoint: API endpoint path
            page: Page number (1-based)
            limit: Records per page

        Returns:
            dict: API response data, or None if all retries failed
        """
        url = f"{self.base_url}{endpoint}"
        params = {'page': page, 'limit': limit}

        for attempt in range(self.max_retries):
            try:
                response = self.session.get(
                    url,
                    params=params,
                    timeout=self.request_timeout
                )

                # Success
                if response.status_code == 200:
                    return response.json()

                # Rate limit (429)
                elif response.status_code == 429:
                    wait_time = calculate_backoff(
                        attempt,
                        self.initial_backoff,
                        is_rate_limit=True
                    )
                    print(f"     Rate limit (429) - waiting {wait_time:.1f}s...")
                    time.sleep(wait_time)
                    self.stats.add_retry()
                    continue

                # Server errors (500, 503)
                elif response.status_code in [500, 503]:
                    wait_time = calculate_backoff(attempt, self.initial_backoff)
                    print(f"     Server error ({response.status_code}) - "
                          f"retry {attempt + 1}/{self.max_retries}, "
                          f"waiting {wait_time:.1f}s...")
                    time.sleep(wait_time)
                    self.stats.add_retry()
                    continue

                # Other errors
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text[:100]}"
                    print(f"   Unknown error: {error_msg}")
                    self.stats.add_failure(page, error_msg)
                    return None

            except requests.exceptions.Timeout:
                wait_time = calculate_backoff(attempt, self.initial_backoff)
                print(f"    Request timeout - retry {attempt + 1}/{self.max_retries}, "
                      f"waiting {wait_time:.1f}s...")
                time.sleep(wait_time)
                self.stats.add_retry()
                continue

            except Exception as e:
                error_msg = f"Request exception: {str(e)}"
                print(f"   {error_msg}")
                self.stats.add_failure(page, error_msg)
                return None

        # All retries exhausted
        print(f"   Page {page} failed after {self.max_retries} retries")
        self.stats.add_failure(page, "Max retries exceeded")
        return None

    def close(self):
        """Close the session"""
        self.session.close()
