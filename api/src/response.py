import json
from copy import deepcopy


def make_response(lambda_execution_id, status=200, body=None):
    if body is None:
        body = dict()
    
    body["id"] = deepcopy(lambda_execution_id)

    response = {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "isBase64Encoded": False,
        "body": json.dumps(body),
    }

    return response
