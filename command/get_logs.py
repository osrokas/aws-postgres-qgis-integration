from src.aws.storage import CloudWatch
import os
from src.decorators import load_env
import boto3


@load_env
def main(log_group_name: str = "/aws/lambda/gpx_lambda_function") -> None:
    """
    Description
    ----------
    Main function to demonstrate CloudWatch log group and stream creation.

    Parameters
    ----------
    :param log_group_name: Name of the CloudWatch log group to create.
    :param log_stream_name: Name of the CloudWatch log stream to create.
    """
    ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.getenv("AWS_REGION")

    logs_client = CloudWatch(
        endpoint_url=ENDPOINT_URL,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )

    log_streams = logs_client.get_log_streams(log_group_name)
    print("Log Streams:", log_streams)

    if not log_streams:
        print("No log streams found.")
        return

    # Get the first log stream name
    stream_name = log_streams[0]["logStreamName"]

    logs_client.get_log_events(log_group_name, stream_name)


if __name__ == "__main__":
    main()
