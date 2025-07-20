"""Setup script for creating AWS services including S3 bucket, Lambda function, and IAM role."""

from importlib.resources import files
import os
import time
import argparse

from tqdm import tqdm

from src.decorators import load_env
from src.utils import create_random_string
from src.aws.storage import S3, IAM, Lambda


@load_env
def main(bucket_name: str, function_name: str, role_name: str) -> None:
    """
    Description
    ----------
    Main function to demonstrate S3 bucket creation and listing.

    Parameters
    ----------
    :param bucket_name: Name of the S3 bucket to create.
    :param function_name: Name of the Lambda function to create.
    :param role_name: Name of the IAM role for the Lambda function.
    """
    # Define the current working directory
    current_path = os.getcwd()

    # Example usage of the S3 class
    ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.getenv("AWS_REGION")

    # Initialize S3 client
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

    # Define the trust policy for the IAM role
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {"Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}
        ],
    }

    # Initialize IAM
    iam_client = IAM()

    # Create the IAM role
    role_arn = iam_client.create_role(role_name, trust_policy)

    # Wait for the role to be created
    time.sleep(5)

    # Initialize Lambda client
    lambda_client = Lambda()

    # Create the Lambda function
    lambda_arn = lambda_client.create_function(
        function_name=function_name,
        role_arn=role_arn,
        lambda_path=os.path.join(current_path, "src", "aws", "lambdas", "lambda_function.py"),
    )

    # Wait for the Lambda function to be created
    time.sleep(5)

    # Add permission for S3 to invoke the Lambda function
    lambda_client.add_permission(
        function_name=function_name, statement_id="s3-trigger-permission", bucket_name=bucket_name
    )

    # Wait for the permission to be added
    time.sleep(5)

    # Invoke the Lambda function to ensure it is set up correctly
    s3_client.lambda_invoke(bucket_name=bucket_name, lambda_arn=lambda_arn)

    # Create a path gpx path
    gpx_path = os.path.join(current_path, "data", "route_framed_synced.gpx")

    # Wait for 20 seconds to ensure the Lambda function is ready
    print("Waiting for 20 seconds...")
    time.sleep(20)

    # Define the number of files to upload
    files_count = range(120)
    print(files_count)
    # Simulate uploading multiple GPX files to S3
    for _ in tqdm(files_count, desc="Uploading GPX files to S3", total=len(files_count)):

        # Create a random string for the file name
        random_string = create_random_string(10)

        # Upload the GPX file to S3
        upload_gpx_path = os.path.join(random_string, f"route_framed_synced.gpx")

        # Upload the file to the S3 bucket
        s3_client.upload_file(gpx_path, bucket_name, upload_gpx_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="S3 Bucket Setup Script")
    parser.add_argument(
        "--bucket_name",
        type=str,
        default="gpx-bucket-aws-test",
        help="Name of the S3 bucket to create.",
    )
    parser.add_argument(
        "--function_name",
        type=str,
        default="gpx_lambda_function",
        help="Name of the Lambda function to create.",
    )
    parser.add_argument(
        "--role_name",
        type=str,
        default="gpx_lambda_role",
        help="Name of the IAM role for the Lambda function.",
    )
    args = parser.parse_args()

    main(
        bucket_name=args.bucket_name,
        function_name=args.function_name,
        role_name=args.role_name,
    )
