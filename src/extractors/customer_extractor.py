"""
Customer data extraction orchestrator
"""

import time
import random
from datetime import datetime

from src.models.statistics import IngestionStats
from src.processors.api_client import RobustAPIClient
from src.processors.csv_writer import StreamingCSVWriter
from src.storage.s3_uploader import upload_to_s3


def extract_all_customers(
    api_base_url,
    api_endpoint,
    api_token,
    s3_bucket,
    s3_prefix,
    max_retries=5,
    initial_backoff=1,
    records_per_page=1000,
    request_timeout=30,
    inter_page_delay=0.5
):
    """
    Main extraction function (ETL Strategy)

    Extract all customer data, clean it, and save to CSV

    Args:
        api_base_url: API base URL
        api_endpoint: API endpoint path
        api_token: Authentication token
        s3_bucket: S3 bucket name
        s3_prefix: S3 key prefix
        max_retries: Maximum retry attempts
        initial_backoff: Initial backoff seconds
        records_per_page: Records per page
        request_timeout: Request timeout seconds
        inter_page_delay: Delay between pages

    Returns:
        str: Local filename of extracted data
    """
    print("\n Starting data extraction (ETL Strategy)...")
    print(f" API: {api_base_url}{api_endpoint}")
    print(f" S3 Target: s3://{s3_bucket}/{s3_prefix}/")
    print("-" * 50 + "\n")

    # Initialize components
    stats = IngestionStats()
    client = RobustAPIClient(
        base_url=api_base_url,
        token=api_token,
        stats=stats,
        max_retries=max_retries,
        initial_backoff=initial_backoff,
        request_timeout=request_timeout
    )

    # Local temp file
    local_filename = f"customers_extract_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    writer = StreamingCSVWriter(local_filename)

    # First request: get total pages
    print(" Fetching metadata...")
    first_page_data = client.fetch_page_with_retry(
        api_endpoint,
        page=1,
        limit=records_per_page
    )

    if not first_page_data:
        print(" Failed to get first page, extraction aborted")
        return None

    # Parse metadata
    metadata = first_page_data.get('metadata', {})
    total_pages = metadata.get('total_pages', 1)

    print(f" Total pages: {total_pages}")
    print(f" Records per page: {records_per_page}")
    print(f" Estimated total records: ~{total_pages * records_per_page:,}\n")

    # Write first page (auto-cleaned)
    records = first_page_data.get('data', [])
    writer.write_records(records)
    stats.pages_requested = 1
    stats.add_success(writer.cleaner.records_accepted)
    print(f" Page 1/{total_pages}: {len(records)} raw → "
          f"{writer.cleaner.records_accepted} cleaned")

    # Fetch remaining pages
    for page in range(2, total_pages + 1):
        stats.pages_requested += 1

        print(f" Page {page}/{total_pages}...", end=" ")

        page_data = client.fetch_page_with_retry(
            api_endpoint,
            page=page,
            limit=records_per_page
        )

        if page_data:
            records = page_data.get('data', [])
            prev_accepted = writer.cleaner.records_accepted
            writer.write_records(records)
            new_accepted = writer.cleaner.records_accepted - prev_accepted
            stats.add_success(new_accepted)
            print(f"✅ {len(records)} raw → {new_accepted} cleaned")
        else:
            print(f"❌ Failed")

        # Rate limit protection with jitter
        time.sleep(inter_page_delay + random.random() * 0.5)

    print(f"\n Data extraction complete! Local file: {local_filename}")

    # Print cleaning summary
    writer.cleaner.print_summary()

    # Upload to S3
    upload_to_s3(local_filename, s3_bucket, s3_prefix)

    # Print final report
    stats.print_report()

    return local_filename
