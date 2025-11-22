"""
Statistics tracking for ingestion processes
"""

import time


class IngestionStats:
    """
    Track extraction process statistics

    Attributes:
        pages_requested: Total pages requested
        successful_pages: Pages successfully fetched
        failed_pages: Pages that failed
        total_retries: Total retry attempts
        records_ingested: Total records successfully ingested
        start_time: Process start timestamp
        errors: List of error messages
    """

    def __init__(self):
        self.pages_requested = 0
        self.successful_pages = 0
        self.failed_pages = 0
        self.total_retries = 0
        self.records_ingested = 0
        self.start_time = time.time()
        self.errors = []

    def add_success(self, records_count):
        """
        Record a successful page fetch

        Args:
            records_count: Number of records in the page
        """
        self.successful_pages += 1
        self.records_ingested += records_count

    def add_failure(self, page, error):
        """
        Record a failed page fetch

        Args:
            page: Page number that failed
            error: Error message
        """
        self.failed_pages += 1
        self.errors.append(f"Page {page}: {error}")

    def add_retry(self):
        """Record a retry attempt"""
        self.total_retries += 1

    def get_execution_time(self):
        """
        Get formatted execution time

        Returns:
            str: Formatted time string (e.g., "5m 30s")
        """
        elapsed = time.time() - self.start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        return f"{minutes}m {seconds}s"

    def get_elapsed_seconds(self):
        """
        Get elapsed time in seconds

        Returns:
            float: Elapsed seconds
        """
        return time.time() - self.start_time

    def print_report(self):
        """Print formatted execution report"""
        print("\n" + "=" * 50)
        print("--- Execution Report ---")
        print("=" * 50)
        print(f"Pages Requested: {self.pages_requested}")
        print(f"Successful Pages: {self.successful_pages}")
        print(f"Failed Pages: {self.failed_pages}")
        print(f"Total Retries: {self.total_retries}")
        print(f"Records Ingested: {self.records_ingested:,}")
        print(f"Execution Time: {self.get_execution_time()}")
        print(f"Format Chosen: CSV (Reason: Streaming efficiency)")
        print(f"Cleaning Strategy: ETL (Clean data before loading)")

        if self.errors:
            print(f"\n  Errors encountered: {len(self.errors)}")
            for error in self.errors[:5]:  # Show first 5 errors
                print(f"   - {error}")

        print("=" * 50 + "\n")

    def to_dict(self):
        """
        Convert statistics to dictionary

        Returns:
            dict: Statistics as dictionary
        """
        return {
            'pages_requested': self.pages_requested,
            'successful_pages': self.successful_pages,
            'failed_pages': self.failed_pages,
            'total_retries': self.total_retries,
            'records_ingested': self.records_ingested,
            'execution_time': self.get_execution_time(),
            'errors': self.errors
        }
