import json
import logging

logging.basicConfig(level=logging.INFO)


def lambda_handler(event, context):
    json_dump = json.dumps(event)
    logging.info("Received event: %s", json_dump)
    return {
        "statusCode": 200,
        "body": json_dump,
    }
