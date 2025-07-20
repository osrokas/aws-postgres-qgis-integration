"""Setup script for creating and listing S3 buckets."""

import os
import time
import argparse

from src.decorators import load_env
from src.utils import create_random_string
from src.aws.storage import S3, CloudWatch, IAM, Lambda


@load_env
def main(
    bucket_name: str = "gpx-bucket-aws-test2",
    log_group_name: str = "gpx-log-group-test2",
    log_stream_name: str = "gpx-log-stream-test2",
) -> None:
    """
    Description
    ----------
    Main function to demonstrate S3 bucket creation and listing.

    Parameters
    ----------
    :param bucket_name: Name of the S3 bucket to create.
    """
    current_path = os.getcwd()

    # Example usage of the S3 class
    ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.getenv("AWS_REGION")

    s3_client = S3(
        endpoint_url=ENDPOINT_URL,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )

    # Create a new bucket
    s3_client.create_bucket(bucket_name)
    print(f"Bucket '{bucket_name}' created successfully.")

    # List all buckets
    buckets = s3_client.list_buckets()
    print("Buckets:", buckets)

    # Create a log group and stream
    logs_client = CloudWatch(
        endpoint_url=ENDPOINT_URL,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )

    logs_client.create_log_group(log_group_name)
    print(f"Log group '{log_group_name}' created successfully.")

    logs_client.create_log_stream(log_group_name, log_stream_name)
    print(f"Log stream '{log_stream_name}' created successfully.")

    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {"Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}
        ],
    }

    iam_client = IAM()

    role_arn = iam_client.create_role("gpx_execution_role_test2", trust_policy)

    lambda_client = Lambda()
    lambda_client.create_function(
        function_name="gpx_lambda_function_test2",
        role_arn=role_arn,
        lambda_path=os.path.join(current_path, "lambda", "lambda_function.py"),
    )

    s3_client.lambda_invoke(function_name="gpx_lambda_function_test2", bucket_name=bucket_name)

    lambda_client.add_permission(
        function_name="gpx_lambda_function_test2", statement_id="AllowS3Invoke", bucket_name=bucket_name
    )

    # Create a path gpx path
    gpx_path = os.path.join(current_path, "data", "route_framed_synced.gpx")

    print("Waiting for 5 seconds...")
    time.sleep(5)
    # Create a random string with 10 characters
    for _ in range(110):
        random_string = create_random_string(10)
        upload_gpx_path = os.path.join(random_string, f"route_framed_synced_{random_string}.gpx")
        s3_client.upload_file(gpx_path, bucket_name, upload_gpx_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="S3 Bucket Setup Script")
    parser.add_argument(
        "--bucket_name",
        type=str,
        default="gpx-bucket-aws-test2",
        help="Name of the S3 bucket to create.",
    )
    args = parser.parse_args()

    main(bucket_name=args.bucket_name)
