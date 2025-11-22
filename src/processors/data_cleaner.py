"""
Data cleaning and validation for ETL pipeline
"""

from src.utils.normalizers import (
    normalize_string,
    normalize_email,
    normalize_phone,
    normalize_name,
    normalize_state,
    normalize_zip_code
)
from src.utils.validators import validate_required_fields, validate_age_range


class DataCleaner:
    """
    Data cleaner for ETL pipeline

    Responsibilities:
        - Validate required fields
        - Normalize data formats
        - Fill default values
        - Track cleaning statistics
    """

    def __init__(self):
        self.records_processed = 0
        self.records_accepted = 0
        self.records_rejected = 0
        self.rejection_reasons = {}

    def clean_record(self, record):
        """
        Clean a single record

        Args:
            record: Raw record dictionary

        Returns:
            dict: Cleaned record, or None if invalid
        """
        self.records_processed += 1

        # Validate required fields
        is_valid, error = validate_required_fields(record, ['id', 'name'])
        if not is_valid:
            self._add_rejection(error)
            return None

        # Clean the record
        cleaned = {}

        try:
            # customer_id: convert to string, strip
            cleaned['customer_id'] = str(record['id']).strip()

            # uuid: preserve as-is
            cleaned['uuid'] = normalize_string(record.get('uuid'))

            # name: strip and title case
            cleaned['name'] = normalize_name(record['name'])

            # email: lowercase, validate format
            cleaned['email'] = normalize_email(record.get('email'))

            # age: validate range 0-120
            _, cleaned['age'] = validate_age_range(record.get('age'))

            # phone: digits only
            cleaned['phone'] = normalize_phone(record.get('phone'))

            # address: strip whitespace
            cleaned['address'] = normalize_string(record.get('address'))

            # city: strip and title case
            cleaned['city'] = normalize_name(record.get('city'))

            # state: uppercase
            cleaned['state'] = normalize_state(record.get('state'))

            # zip_code: digits and hyphens only
            cleaned['zip_code'] = normalize_zip_code(record.get('zip_code'))

            # Handle any additional fields (generic cleaning)
            for key, value in record.items():
                if key not in cleaned:
                    cleaned[key] = normalize_string(value)

            self.records_accepted += 1
            return cleaned

        except Exception as e:
            self._add_rejection(f"Cleaning error: {str(e)}")
            return None

    def _add_rejection(self, reason):
        """
        Record rejection reason

        Args:
            reason: Rejection reason string
        """
        self.records_rejected += 1
        self.rejection_reasons[reason] = self.rejection_reasons.get(reason, 0) + 1

    def print_summary(self):
        """Print cleaning summary"""
        if self.records_processed == 0:
            print("\n No records processed")
            return

        accept_pct = self.records_accepted / self.records_processed * 100
        reject_pct = self.records_rejected / self.records_processed * 100

        print(f"\n Data Cleaning Summary (ETL Strategy):")
        print(f"  Total records processed: {self.records_processed:,}")
        print(f"   Accepted: {self.records_accepted:,} ({accept_pct:.1f}%)")
        print(f"   Rejected: {self.records_rejected:,} ({reject_pct:.1f}%)")

        if self.rejection_reasons:
            print(f"\n  Rejection reasons:")
            sorted_reasons = sorted(
                self.rejection_reasons.items(),
                key=lambda x: x[1],
                reverse=True
            )
            for reason, count in sorted_reasons:
                print(f"    - {reason}: {count:,}")

    def get_summary(self):
        """
        Get cleaning summary as dictionary

        Returns:
            dict: Cleaning statistics
        """
        return {
            'records_processed': self.records_processed,
            'records_accepted': self.records_accepted,
            'records_rejected': self.records_rejected,
            'rejection_reasons': self.rejection_reasons
        }

    def reset(self):
        """Reset all statistics"""
        self.records_processed = 0
        self.records_accepted = 0
        self.records_rejected = 0
        self.rejection_reasons = {}
