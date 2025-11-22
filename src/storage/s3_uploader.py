"""
S3 upload functionality
"""

import boto3
from datetime import datetime


def upload_to_s3(local_filename, bucket, prefix):
    """
    Upload file to S3 with date-based partitioning

    Args:
        local_filename: Local file path
        bucket: S3 bucket name
        prefix: S3 key prefix

    Returns:
        str: S3 URI if successful, None if failed
    """
    print("\n Uploading to S3...")

    try:
        s3_client = boto3.client('s3')

        # S3 key: prefix/date=YYYY-MM-DD/filename
        date_str = datetime.now().strftime('%Y-%m-%d')
        s3_key = f"{prefix}/date={date_str}/{local_filename}"

        # Upload
        s3_client.upload_file(
            local_filename,
            bucket,
            s3_key
        )

        s3_uri = f"s3://{bucket}/{s3_key}"
        print(f" Upload successful!")
        print(f" S3 path: {s3_uri}")

        return s3_uri

    except Exception as e:
        print(f" S3 upload failed: {str(e)}")
        print(f" Local file saved: {local_filename}")
        return None


def upload_to_s3_with_metadata(local_filename, bucket, prefix, metadata=None):
    """
    Upload file to S3 with custom metadata

    Args:
        local_filename: Local file path
        bucket: S3 bucket name
        prefix: S3 key prefix
        metadata: Dictionary of metadata to attach

    Returns:
        str: S3 URI if successful, None if failed
    """
    print("\n Uploading to S3 with metadata...")

    try:
        s3_client = boto3.client('s3')

        # S3 key: prefix/date=YYYY-MM-DD/filename
        date_str = datetime.now().strftime('%Y-%m-%d')
        s3_key = f"{prefix}/date={date_str}/{local_filename}"

        # Prepare extra args
        extra_args = {}
        if metadata:
            extra_args['Metadata'] = {
                str(k): str(v) for k, v in metadata.items()
            }

        # Upload
        s3_client.upload_file(
            local_filename,
            bucket,
            s3_key,
            ExtraArgs=extra_args if extra_args else None
        )

        s3_uri = f"s3://{bucket}/{s3_key}"
        print(f" Upload successful!")
        print(f" S3 path: {s3_uri}")

        return s3_uri

    except Exception as e:
        print(f" S3 upload failed: {str(e)}")
        print(f" Local file saved: {local_filename}")
        return None
