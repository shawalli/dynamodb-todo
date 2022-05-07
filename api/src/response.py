import json
from copy import deepcopy


def is_error_response(status_code):
    return not (200 <= status_code < 400)


def make_response(lambda_execution_id, status_code=200, body=None, error=None, developer_text=None):
    if body is not None:
        body = deepcopy(body)

    if is_error_response(status_code):
        if body is None:
            body = dict()

        if error is None:
            raise ValueError("non-success response must have error code")

        body.update({
            "id": lambda_execution_id,
            "error": error,
            "developerText": "",
        })

        if developer_text is not None:
            body["developerText"] = developer_text

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
