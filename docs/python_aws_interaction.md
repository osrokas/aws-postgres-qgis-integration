# Python and AWS Interaction Documentation

1. Create docker image to simulate AWS environment with LocalStack:
   ```bash
   docker compose up -d
   ```

3. Define environment variables in `.env` file from `.env-example` (development only):

2. Run Python script to setup AWS environment:
   ```bash
   python -m command.setup_aws --bucket_name <bucket_name> --function_name <function_name> --role_name <role_name>
   ```
4. Run following command to execute the Python script that interacts with AWS:
   ```bash
   python -m command.download_gpx --log_group_name <log_group_name> --log_stream_name <log_stream_name> --download_dir <download_dir> --events_count <events_count> --earliest --latest
   ```

Example command:
```bash
python -m command.download_gpx --log_group_name /aws/lambda/gpx_lambda_function --log_stream_name 2025/07/21/[$LATEST]3cb0c567f6f38e4a08c06eecdaae086d --download_dir C:\dev\aws-postgres-qgis-integration\data\gpx_s3_data --events_count 100 --latest
```

## Known Issues
**command.setup_aws** creates multiple AWS Lambda functions with the same name, which creates multiple log streams in CloudWatch. In that case **command.download_gpx** will not work as expected. You need to manualy define log stream name after each setup of AWS environment. It only downloads those gpx files that are in the specified log stream.