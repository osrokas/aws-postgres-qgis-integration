"""This module provides interactions with AWS"""

import boto3


class AWS:
    def __init__(
        self,
        service_name,
        endpoint_url="http://localhost:4566",
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name="us-east-1",
    ):
        self.service_name = service_name
        self.endpoint_url = endpoint_url
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name

        self.client = boto3.client(
            service_name,
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.region_name,
        )


class S3(AWS):
    def __init__(self, service_name="s3", **kwargs):
        super().__init__(service_name, **kwargs)

    def list_buckets(self):
        """List all S3 buckets."""
        response = self.client.list_buckets()
        return response.get("Buckets", [])

    def create_bucket(self, bucket_name):
        """Create a new S3 bucket."""
        self.client.create_bucket(Bucket=bucket_name)
        return f"Bucket {bucket_name} created successfully."

    def upload_file(self, file_name, bucket_name, object_name=None):
        """Upload a file to an S3 bucket."""
        if object_name is None:
            object_name = file_name
        self.client.upload_file(file_name, bucket_name, object_name)
        return f"File {file_name} uploaded to bucket {bucket_name} as {object_name}."

    def list_files(self, bucket_name):
        """List files in an S3 bucket."""
        response = self.client.list_objects_v2(Bucket=bucket_name)
        if "Contents" in response:
            return [obj["Key"] for obj in response["Contents"]]
        else:
            return []


class CloudWatch(AWS):
    def __init__(self, service_name="logs", **kwargs):
        super().__init__(service_name, **kwargs)

    def create_log_group(self, log_group_name):
        """Create a CloudWatch log group."""
        self.client.create_log_group(logGroupName=log_group_name)
        return f"Log group {log_group_name} created successfully."

    def create_log_stream(self, log_group_name, log_stream_name):
        """Create a CloudWatch log stream."""
        self.client.create_log_stream(logGroupName=log_group_name, logStreamName=log_stream_name)
        return f"Log stream {log_stream_name} created in group {log_group_name}."


if __name__ == "__main__":
    # Example usage
    aws_storage = S3()

    retrieved_files = aws_storage.list_files("my-docker-bucket")
    print("Files in bucket:", retrieved_files)
