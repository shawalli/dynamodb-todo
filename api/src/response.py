import json
from copy import deepcopy


def is_error_response(status_code):
    return 200 < status_code < 400


def make_response(lambda_execution_id, status_code=200, body=None):
    if not is_error_response(status_code):
        if body is None:
            body = dict()

        body["id"] = deepcopy(lambda_execution_id)

    response = {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Origin": "*",
        },
        "isBase64Encoded": False,
    }

    if body is not None:
        response["body"] = json.dumps(body)
        response["headers"].update({"Content-Type": "application/json"})

    return response
