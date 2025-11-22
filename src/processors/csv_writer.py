"""
Streaming CSV writer with integrated data cleaning
"""

import csv


class StreamingCSVWriter:
    """
    Streaming CSV writer with ETL integration

    Features:
        - Row-by-row writing (memory efficient)
        - Automatic data cleaning before write
        - Tracks cleaning statistics
    """

    def __init__(self, filename, cleaner=None):
        """
        Initialize CSV writer

        Args:
            filename: Output filename
            cleaner: DataCleaner instance (optional, creates one if not provided)
        """
        self.filename = filename
        self.header_written = False
        self.fieldnames = None

        # Use provided cleaner or create new one
        if cleaner is None:
            from src.processors.data_cleaner import DataCleaner
            self.cleaner = DataCleaner()
        else:
            self.cleaner = cleaner

    def write_records(self, records):
        """
        Clean and write records to CSV

        Args:
            records: List of raw record dictionaries
        """
        if not records:
            return

        # ETL: Clean data first
        cleaned_records = []
        for record in records:
            cleaned = self.cleaner.clean_record(record)
            if cleaned:  # Only keep valid records
                cleaned_records.append(cleaned)

        if not cleaned_records:
            return

        # Determine fieldnames from first batch
        if not self.fieldnames:
            all_keys = set()
            for record in cleaned_records:
                all_keys.update(record.keys())
            self.fieldnames = sorted(list(all_keys))

        # Append mode after header is written
        mode = 'a' if self.header_written else 'w'

        with open(self.filename, mode, newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(
                f,
                fieldnames=self.fieldnames,
                extrasaction='ignore'
            )

            # Write header once
            if not self.header_written:
                writer.writeheader()
                self.header_written = True

            # Write cleaned data
            for record in cleaned_records:
                row = {key: record.get(key, 'N/A') for key in self.fieldnames}
                writer.writerow(row)

    def get_cleaner(self):
        """
        Get the data cleaner instance

        Returns:
            DataCleaner: The cleaner instance
        """
        return self.cleaner

    def get_records_written(self):
        """
        Get count of records written

        Returns:
            int: Number of records written
        """
        return self.cleaner.records_accepted
