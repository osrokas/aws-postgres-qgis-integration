"""This module provides interactions with AWS"""

import io
import json
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
        """
        Description:
        ------------
        Initialize the S3 service client.

        Parameters:
        -----------
        :param service_name: Name of the AWS service (default is 's3').
        :param endpoint_url: URL of the AWS service endpoint (default is 'http://localhost:4566').
        :param aws_access_key_id: AWS access key ID (default is 'test').
        :param aws_secret_access_key: AWS secret access key (default is 'test').
        :param region_name: AWS region name (default is 'us-east-1').
        """

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
        :param lambda_arn: ARN of the Lambda function to invoke.
        """
        # Set the notification configuration for the S3 bucket to trigger the Lambda function
        self.client.put_bucket_notification_configuration(
            Bucket=bucket_name,
            NotificationConfiguration={
                "LambdaFunctionConfigurations": [{"LambdaFunctionArn": lambda_arn, "Events": ["s3:ObjectCreated:*"]}]
            },
        )

    def download_file(self, bucket_name: str, object_name: str, download_path: str) -> None:
        """
        Description:
        ------------
        Download a file from an S3 bucket.

        Parameters:
        -----------
        :param bucket_name: Name of the bucket to download from.
        :param object_name: S3 object name to download.
        :param download_path: Path to save the downloaded file.
        """
        self.client.download_file(bucket_name, object_name, download_path)


class CloudWatch(AWS):
    def __init__(self, service_name="logs", **kwargs):
        super().__init__(service_name, **kwargs)
        """
        Description:
        ------------
        Initialize the CloudWatch service client.

        Parameters:
        -----------
        :param service_name: Name of the AWS service (default is 'logs').
        :param endpoint_url: URL of the AWS service endpoint (default is 'http://localhost:4566').
        :param aws_access_key_id: AWS access key ID (default is 'test').
        :param aws_secret_access_key: AWS secret access key (default is 'test').
        :param region_name: AWS region name (default is 'us-east-1').
        """

    def create_log_group(self, log_group_name: str) -> None:
        """
        Description:
        ------------
        Create a CloudWatch log group.

        Parameters:
        -----------
        :param log_group_name: Name of the log group to create.
        """
        # Create a new log group
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
        # Get log streams for the specified log group
        streams = self.client.describe_log_streams(
            logGroupName=log_group_name, orderBy="LastEventTime", descending=True
        )
        log_streams = streams.get("logStreams", [])

        return log_streams

    def get_log_events(
        self, log_group_name: str, log_stream_name: str, earliest: bool = False, events_count: int = 10
    ) -> list:
        """
        Description:
        ------------
        Get log events from a CloudWatch log stream.

        Parameters:
        -----------
        :param log_group_name: Name of the log group to retrieve logs from.
        :param log_stream_name: Name of the log stream to retrieve logs from.
        :param earliest: If True, get the earliest logs. Default is False.
        :param events_count: Number of log events to retrieve.

        Returns:
        --------
        :return: List of log events containing GPX files.
        """
        # Multiply events_count by 4 to ensure we get enough events
        events_count *= 4

        # Get response from CloudWatch logs
        response = self.client.get_log_events(
            logGroupName=log_group_name, logStreamName=log_stream_name, startFromHead=earliest, limit=events_count
        )

        # Get events from the response
        events = response.get("events", [])
        if not events:
            print(f"No log events found in stream {log_stream_name} of group {log_group_name}.")
            return []

        # Create a placeholder for GPS files
        gps_files = []

        # Iterate over the events and extract GPS files
        for event in events:
            # Get the event message
            event_message = event.get("message", "")
            # If the event message is empty continue to the next iteration
            if not event_message:
                continue
            # Check if the event message contains a GPX file
            if "route_framed_synced.gpx" in event_message:
                # Parse the JSON data from the event message
                json_data = json.loads(event_message)
                # Get the records from the JSON data
                records = json_data.get("Records", [])
                # Iterate over the records and extract GPX files
                for record in records:
                    # Get the S3 bucket name
                    s3_bucket = record["s3"]["bucket"]["name"]
                    # Get the S3 object key (file name)
                    s3_key = record["s3"]["object"]["key"]
                    # Parse the S3 key to define correctly formatted file name
                    s3_key = s3_key.replace("%5C", "\\")
                    # Get the event timestamp
                    event_timestamp = record["eventTime"]
                    # Create a dictionary with GPX file information
                    gps_files.append(({"bucket": s3_bucket, "filename": s3_key, "event_timestamp": event_timestamp}))

        return gps_files

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
        # Create a new log stream in the specified log group
        self.client.create_log_stream(logGroupName=log_group_name, logStreamName=log_stream_name)
        print(f"Log stream {log_stream_name} created in group {log_group_name}.")


class Lambda(AWS):
    def __init__(self, service_name: str = "lambda", **kwargs):
        super().__init__(service_name, **kwargs)
        """
        Description:
        ------------
        Initialize the Lambda service client.

        Parameters:
        -----------
        :param service_name: Name of the AWS service (default is 'lambda').
        :param endpoint_url: URL of the AWS service endpoint (default is 'http://localhost:4566').
        :param aws_access_key_id: AWS access key ID (default is 'test').
        :param aws_secret_access_key: AWS secret access key
        :param region_name: AWS region name (default is 'us-east-1').
        """

    def __load_lambda_code(self, lambda_path: str, py_function: str = "lambda_function.py") -> io.BytesIO:
        """
        Description:
        ------------
        Load the Lambda function code into a zip file in memory.

        Parameters:
        -----------
        :param lambda_path: Path to the Lambda function code file.
        :param py_function: Name of the Python function file to include in the zip (default is 'lambda_function.py').

        Returns:
        --------
        :return: BytesIO object containing the zipped code.
        """
        # Create a BytesIO buffer to hold the zip file
        zip_buffer = io.BytesIO()

        # Read the Lambda function code from the specified path
        with open(lambda_path, "r") as f:
            lambda_code = f.read()

        # Create a zip file in memory
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            # Write the Lambda function code to the zip file
            zipinfo = zipfile.ZipInfo(py_function)
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
        :param lambda_path: Path to the Lambda function code file.

        Returns:
        --------
        :return: ARN of the created Lambda function.
        """
        # Zip the Lambda function code into memory
        zipped_code = self.__load_lambda_code(lambda_path)

        # Create the Lambda function using the zipped code
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

        # Get the AWS resource
        lambda_arn = self.client.get_function(FunctionName=function_name)["Configuration"]["FunctionArn"]
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
        # Add permission for the S3 bucket to invoke the Lambda function
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

        Returns:
        --------
        :return: ARN of the created IAM role.
        """
        try:
            # Create the IAM role with the specified trust policy
            role_response = self.client.create_role(
                RoleName=role_name, AssumeRolePolicyDocument=json.dumps(trust_policy)
            )
            # Attach the AWSLambdaBasicExecutionRole policy to the role
            self.client.attach_role_policy(
                RoleName=role_name, PolicyArn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
            )
            # Get the ARN of the created role
            role_arn = role_response["Role"]["Arn"]
            print(f"IAM role {role_name} created successfully with ARN: {role_arn}")

        except self.client.exceptions.EntityAlreadyExistsException:
            print(f"IAM role {role_name} already exists.")
            # If the role already exists, retrieve its ARN
            role_arn = self.client.get_role(RoleName=role_name)["Role"]["Arn"]

        return role_arn
