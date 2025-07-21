import json


def lambda_handler(event, context):
    """
    Description
    ----------
    Lambda function to process S3 events and extract GPX files.

    Parameters
    ----------
    :param event: Event data passed to the Lambda function.
    :param context: Context object providing runtime information.
    """
    json_dump = json.dumps(event)
    print(json_dump)
