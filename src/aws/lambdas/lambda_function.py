import json
import logging

logging.basicConfig(level=logging.INFO)


def lambda_handler(event, context):
    json_dump = json.dumps(event)
    print(json_dump)
