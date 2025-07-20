from src.aws.storage import CloudWatch
import os
from src.decorators import load_env


@load_env
def main(log_group_name: str = "gpx-log-group-test2", log_stream_name: str = "gpx-log-stream-test2") -> None:
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

    #     Log group my-log-group1 created successfully.
    # Log group 'my-log-group1' created successfully.
    # Log stream my-log-stream2 created in group my-log-group1.
    # Log stream 'my-log-stream2' created successfully.

    logs_client.get_all_log_groups(log_group_name, log_stream_name)


if __name__ == "__main__":
    main()
