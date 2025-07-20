"""This module provides interactions with AWS"""

import io
import json
import os
import zipfile

import boto3


class AWS:
    def __init__(
        self,
        service_name: str = "s3",
        endpoint_url: str = "http://localhost:4566",
        aws_access_key_id: str = "test",
        aws_secret_access_key: str = "test",
        region_name: str = "us-east-1",
    ):
        """
        Description:
        ------------
        Initialize the AWS service client.

        Parameters:
        -----------
        :param service_name: Name of the AWS service (default is 's3').
        :param endpoint_url: URL of the AWS service endpoint (default is 'http://localhost:4566').
        :param aws_access_key_id: AWS access key ID (default is 'test').
        :param aws_secret_access_key: AWS secret access key (default is 'test').
        :param region_name: AWS region name (default is 'us-east-1').
        """
        self.service_name = service_name
        self.endpoint_url = endpoint_url
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name

        # Create service client
        self.client = boto3.client(
            service_name,
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.region_name,
        )


class S3(AWS):
    def __init__(self, service_name: str = "s3", **kwargs):
        super().__init__(service_name, **kwargs)

    def create_bucket(self, bucket_name: str) -> None:
        """
        Description:
        ------------
        Create a new S3 bucket.

        Parameters:
        -----------
        :param bucket_name: bucket name to be created.
        """
        # Create a new S3 bucket
        self.client.create_bucket(Bucket=bucket_name)

    def list_buckets(self) -> list:
        """
        Description:
        ------------
        List all S3 buckets.

        Returns:
        --------
        :return: List of bucket names.
        """
        # Get response from S3 service
        response = self.client.list_buckets()

        # Extract bucket names from the response
        buckets = response.get("Buckets", [])

        # Iterate over the buckets and get their names
        bucket_names = [bucket["Name"] for bucket in buckets]

        return bucket_names

    def upload_file(self, file_name: str, bucket_name: str, object_name: str) -> None:
        """
        Description:
        ------------
        Upload a file to an S3 bucket.

        Parameters:
        -----------
        :param file_name: Path to the file to upload.
        :param bucket_name: Name of the bucket to upload to.
        :param object_name: S3 object name. If not specified, file_name is used.
        """
        if object_name is None:
            object_name = file_name
        self.client.upload_file(file_name, bucket_name, object_name)

    def list_files(self, bucket_name: str) -> list:
        """
        Description:
        ------------
        List files in an S3 bucket.

        Parameters:
        -----------
        :param bucket_name: Name of the bucket to list files from.

        Returns:
        --------
        :return: List of file names in the bucket.
        """
        # Create placeholder for file names
        file_names = []

        # List objects in the specified S3 bucket
        response = self.client.list_objects_v2(Bucket=bucket_name)

        # Check if 'Contents' is in the response and return the list of file names
        if "Contents" in response:
            file_names = [obj["Key"] for obj in response["Contents"]]

        return file_names

    def lambda_invoke(self, bucket_name: str, lambda_arn: str) -> None:
        """
        Description:
        ------------
        Invoke a Lambda function.

        Parameters:
        -----------
        :param function_name: Name of the Lambda function to invoke.
        :param payload: Payload to send to the Lambda function.

        Returns:
        --------
        :return: Response from the Lambda function.
        """
        # 5. Add S3 event notification to invoke Lambda

        self.client.put_bucket_notification_configuration(
            Bucket=bucket_name,
            NotificationConfiguration={
                "LambdaFunctionConfigurations": [{"LambdaFunctionArn": lambda_arn, "Events": ["s3:ObjectCreated:*"]}]
            },
        )


class CloudWatch(AWS):
    def __init__(self, service_name="logs", **kwargs):
        super().__init__(service_name, **kwargs)

    def create_log_group(self, log_group_name: str) -> None:
        """
        Description:
        ------------
        Create a CloudWatch log group.

        Parameters:
        -----------
        :param log_group_name: Name of the log group to create.
        """

        self.client.create_log_group(logGroupName=log_group_name)
        print(f"Log group {log_group_name} created successfully.")

    def get_log_streams(self, log_group_name: str) -> list:
        """
        Description:
        ------------
        Get log streams for a specific CloudWatch log group.

        Parameters:
        -----------
        :param log_group_name: Name of the log group to retrieve log streams from.

        Returns:
        --------
        :return: List of log streams.
        """
        streams = self.client.describe_log_streams(
            logGroupName=log_group_name, orderBy="LastEventTime", descending=True
        )
        return streams["logStreams"]

    def get_log_events(self, log_group_name: str, log_stream_name: str) -> None:
        """
        Description:
        ------------
        Get log events from a CloudWatch log stream.

        Parameters:
        -----------
        :param log_group_name: Name of the log group to retrieve logs from.
        :param log_stream_name: Name of the log stream to retrieve logs from.
        """
        response = self.client.get_log_events(logGroupName=log_group_name, logStreamName=log_stream_name)
        for event in response["events"]:
            print(event["message"])

    def create_log_stream(self, log_group_name: str, log_stream_name: str) -> None:
        """
        Description:
        ------------
        Create a CloudWatch log stream.

        Parameters:
        -----------
        :param log_group_name: Name of the log group to create the stream in.
        :param log_stream_name: Name of the log stream to create.
        """
        self.client.create_log_stream(logGroupName=log_group_name, logStreamName=log_stream_name)
        print(f"Log stream {log_stream_name} created in group {log_group_name}.")

    def get_all_logs(self, log_group_name: str, log_stream_name: str) -> None:
        """
        Description:
        ------------
        Get all logs from a CloudWatch log group.

        Parameters:
        -----------
        :param log_group_name: Name of the log group to retrieve logs from.

        Returns:
        --------
        :return: List of log events.
        """
        response = self.client.get_log_events(logGroupName=log_group_name, logStreamName=log_stream_name)
        print(response)
        for stream in response["events"]:
            stream_name = stream["logStreamName"]
            print(f"--- Logs from: {stream_name} ---")
            events = self.client.get_log_events(
                logGroupName=log_group_name, logStreamName=stream_name, startFromHead=True
            )
            for e in events["events"]:
                print(e["message"])
        return None

    def get_all_log_groups(self, log_group_name: str, log_stream_name: str):
        """
        Description:
        ------------
        Get all CloudWatch log groups.

        Returns:
        --------
        :return: List of log group names.
        """
        response = self.client.get_log_events(log_group_name, log_stream_name, startFromHead=True)
        for e in response:
            print(e["message"])


class Lambda(AWS):
    def __init__(self, service_name: str = "lambda", **kwargs):
        super().__init__(service_name, **kwargs)

        # Create zip in memory

    def __load_lambda_code(self, lambda_path: str) -> io.BytesIO:
        """
        Description:
        ------------
        Load the Lambda function code into a zip file in memory.

        Parameters:
        -----------
        :param lambda_code: The code for the Lambda function.

        Returns:
        --------
        :return: BytesIO object containing the zipped code.
        """
        # Create a BytesIO buffer to hold the zip file
        zip_buffer = io.BytesIO()

        with open(lambda_path, "r") as f:
            lambda_code = f.read()

        # Create a zip file in memory
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            zipinfo = zipfile.ZipInfo("lambda_function.py")
            zipinfo.external_attr = 0o644 << 16  # Set file permissions
            zip_file.writestr(zipinfo, lambda_code)

        # Seek to the beginning of the BytesIO buffer before returning
        zip_buffer.seek(0)
        return zip_buffer

    def create_function(self, function_name: str, role_arn: str, lambda_path: str) -> str:
        """
        Description:
        ------------
        Create a Lambda function.

        Parameters:
        -----------
        :param function_name: Name of the Lambda function to create.
        :param role_arn: ARN of the IAM role that Lambda assumes when it executes the function.
        :param zipped_code: Zipped code for the Lambda function.
        """
        zipped_code = self.__load_lambda_code(lambda_path)

        self.client.create_function(
            FunctionName=function_name,
            Runtime="python3.10",
            Role=role_arn,
            Handler="lambda_function.lambda_handler",
            Code={"ZipFile": zipped_code.read()},
            Description="Logs S3 upload events",
            Timeout=30,
            MemorySize=128,
        )

        lambda_arn = self.client.get_function(FunctionName=function_name)["Configuration"]["FunctionArn"]

        print(lambda_arn)
        print(f"Lambda function {function_name} created successfully.")

        return lambda_arn

    def add_permission(self, function_name: str, statement_id: str, bucket_name: str) -> None:
        """
        Description:
        ------------
        Add permission to a Lambda function.

        Parameters:
        -----------
        :param function_name: Name of the Lambda function to add permission to.
        :param statement_id: Unique identifier for the statement.
        :param bucket_name: Name of the S3 bucket that can invoke the Lambda function.
        """
        self.client.add_permission(
            FunctionName=function_name,
            StatementId=statement_id,
            Action="lambda:InvokeFunction",
            Principal="s3.amazonaws.com",
            SourceArn=f"arn:aws:s3:::{bucket_name}",
            SourceAccount="000000000000",
        )
        print(f"Permission added to Lambda function {function_name} for bucket {bucket_name}.")
        print("AWS client initialized for service:", self.service_name)


class IAM(AWS):
    def __init__(self, service_name: str = "iam", **kwargs):
        super().__init__(service_name, **kwargs)

    def create_role(self, role_name: str, trust_policy: dict) -> str:
        """
        Description:
        ------------
        Create an IAM role.

        Parameters:
        -----------
        :param role_name: Name of the IAM role to create.
        :param trust_policy: Policy that grants an entity permission to assume the role.
        """
        try:
            role_response = self.client.create_role(
                RoleName=role_name, AssumeRolePolicyDocument=json.dumps(trust_policy)
            )

            self.client.attach_role_policy(
                RoleName=role_name, PolicyArn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
            )

            role_arn = role_response["Role"]["Arn"]

            print(f"IAM role {role_name} created successfully with ARN: {role_arn}")
        except self.client.exceptions.EntityAlreadyExistsException:
            print(f"IAM role {role_name} already exists.")
            role_arn = self.client.get_role(RoleName=role_name)["Role"]["Arn"]

        return role_arn
