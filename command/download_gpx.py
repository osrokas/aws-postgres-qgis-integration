"""This script downloads GPX files from AWS S3 based on CloudWatch logs."""

import os
import argparse

from tqdm import tqdm

from src.decorators import load_env
from src.aws.storage import CloudWatch, S3


@load_env
def main(
    log_group_name: str, log_stream_name: str, download_dir: str, events_count: int = 100, earliest: bool = False
) -> None:
    """
    Description
    ----------
    Main function to demonstrate CloudWatch log group and stream creation.

    Parameters
    ----------
    :param log_group_name: Name of the CloudWatch log group to create.
    :param log_stream_name: Name of the CloudWatch log stream to create.
    :param download_dir: Directory to download GPX files to.
    :param events_count: Number of events to retrieve from CloudWatch logs.
    :param earliest: If True, retrieves the earliest log events; otherwise, retrieves the most recent log events.
    """
    # Define credentials and endpoint URL
    ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.getenv("AWS_REGION")

    # Initialize CloudWatch client
    logs_client = CloudWatch(
        endpoint_url=ENDPOINT_URL,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )

    # Initialize S3 client
    s3_client = S3(
        endpoint_url=ENDPOINT_URL,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )

    # Get log stream group
    log_streams = logs_client.get_log_streams(log_group_name)
    print("Log Streams:", log_streams)

    # Check if log streams exist
    if not log_streams:
        print("No log streams found.")
        return

    # Get the latest log stream
    gpx_files = logs_client.get_log_events(
        log_group_name, log_stream_name, earliest=earliest, events_count=events_count
    )

    if not gpx_files:
        print("No GPX files found in the log stream.")
        return

    # Create download directory if it does not exist
    os.makedirs(download_dir, exist_ok=True)

    print("GPX Files in Log Stream:")
    for gpx_file in tqdm(gpx_files, desc="Processing GPX files", total=len(gpx_files)):
        # Get the filename name
        file_name = gpx_file.get("filename")
        # Get file name and bucket name
        bucket_name = gpx_file.get("bucket")
        # Define the download path
        download_path = os.path.join(download_dir, file_name)
        # Define subdirectory for gpx file
        gpx_dir = os.path.split(file_name)
        # Create subdirectory if it does not exist
        os.makedirs(os.path.join(download_dir, gpx_dir[0]), exist_ok=True)
        # Download the file from S3
        s3_client.download_file(bucket_name, file_name, download_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get CloudWatch logs.")
    parser.add_argument(
        "--log_group_name",
        type=str,
        help="Name of the CloudWatch log group to create.",
    )
    parser.add_argument(
        "--log_stream_name",
        type=str,
        help="Name of the CloudWatch log stream to create.",
    )
    parser.add_argument(
        "--download_dir",
        type=str,
        help="Directory to download GPX files to.",
    )
    parser.add_argument(
        "--events_count",
        type=int,
        default=100,
        help="Number of events to retrieve from CloudWatch logs.",
    )
    parser.add_argument(
        "--earliest",
        action="store_true",
        help="Retrieve the earliest log events.",
    )
    # store false
    parser.add_argument(
        "--latest",
        dest="earliest",
        action="store_false",
        help="Retrieve the latest log events.",
    )
    parser.set_defaults(earliest=False)

    args = parser.parse_args()
    main(
        log_group_name=args.log_group_name,
        log_stream_name=args.log_stream_name,
        download_dir=args.download_dir,
        events_count=args.events_count,
        earliest=args.earliest,
    )
