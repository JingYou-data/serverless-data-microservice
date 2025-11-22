"""
============================================================
Unstable API Data Extraction Script (ETL Strategy)
Production-ready robust implementation
============================================================

Architecture Decision Record (ADR)

Decision 1: Output Format - CSV
------------------------------
Rationale:
1. Memory efficiency: Supports streaming writes, row by row, no need to load all records
2. Recoverability: Can resume from last written position if program crashes
3. Universality: Any tool (Excel, Pandas, SQL) can read directly
4. Simplicity: No complex batch logic required (unlike Parquet)

Trade-offs:
- JSON requires building complete structure in memory or using non-standard .ndjson
- Parquet requires batching and more dependencies
- CSV is most stable for "extract first, process later" strategy

Decision 2: Cleaning Strategy - ETL (Extract-Transform-Load)
------------------------------
Rationale:
1. Data quality first: Ensures S3 data is clean and immediately usable
2. Downstream efficiency: Analysts can use data directly without cleaning
3. Storage optimization: Don't store useless dirty data, save storage costs
4. Production ready: S3 data can be used directly for reports and models

Implementation:
- Validate required fields (customer_id, name)
- Standardize formats (lowercase email, strip whitespace, digits-only phone)
- Fill default values for missing fields
- Validate ranges (age 0-120)
- Track rejected records and reasons

Trade-offs:
- Cleaning logic needs careful testing
- Cannot keep original dirty data for audit
- But ensures data quality and improves downstream efficiency
============================================================
"""

from config import (
    API_BASE_URL, API_ENDPOINT, API_TOKEN,
    S3_BUCKET, S3_PREFIX,
    MAX_RETRIES, INITIAL_BACKOFF, RECORDS_PER_PAGE,
    REQUEST_TIMEOUT, INTER_PAGE_DELAY,
    print_config
)

from src.extractors.customer_extractor import extract_all_customers


def main():
    """Main entry point"""
    # Print configuration
    print_config()

    # Run extraction
    extract_all_customers(
        api_base_url=API_BASE_URL,
        api_endpoint=API_ENDPOINT,
        api_token=API_TOKEN,
        s3_bucket=S3_BUCKET,
        s3_prefix=S3_PREFIX,
        max_retries=MAX_RETRIES,
        initial_backoff=INITIAL_BACKOFF,
        records_per_page=RECORDS_PER_PAGE,
        request_timeout=REQUEST_TIMEOUT,
        inter_page_delay=INTER_PAGE_DELAY
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nUser interrupted program")
    except Exception as e:
        print(f"\n\nProgram error: {str(e)}")
        import traceback
        traceback.print_exc()
