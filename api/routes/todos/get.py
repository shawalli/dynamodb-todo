from dataclasses import field
from typing import Optional

from boto3.dynamodb.conditions import Key
from marshmallow_dataclass import dataclass

from api import errorcodes
from api.dynamodb import TABLE, user_exists
from api.log import get_logger
from api.response import make_response
from api.types import BaseRequest

LOG = get_logger()


@dataclass
class GetPathParams(BaseRequest):
    user_id: str = field(metadata={"data_key": "userId"})
    todo_id: Optional[str] = field(metadata={"data_key": "todoId"})


def handle(event, context):
    """Gets one todo if todo-id given, else all user todos."""
    path_params = GetPathParams.load(event["pathParameters"])

    LOG.info(f'getting todo resource(s) for username "{path_params.user_id}"')

    if not user_exists(path_params.user_id):
        LOG.error(f'username "{path_params.user_id}" does not exist.')
        return make_response(context.aws_request_id, 400, body={"error": errorcodes.RESOURCE_NOT_EXIST, "developerText": ""})

    items = []
    if path_params.todo_id is not None:
        LOG.info(f'getting todo with id "{path_params.todo_id}"')
        todo_request = {
            "userId": path_params.user_id,
            "userItem": f"todo#{path_params.todo_id}",
        }

        results = TABLE.get_item(Key=todo_request)
        if "Item" in results:
            items.append(results["Item"])
        else:
            LOG.error(f'todo with id "{path_params.todo_id}" does not exist.')
            return make_response(context.aws_request_id, 404, body={"error": errorcodes.RESOURCE_NOT_EXIST, "developerText": ""})

    else:
        LOG.info("getting all todos for username")
        results = TABLE.query(
            KeyConditionExpression=Key("userId").eq(path_params.user_id) & Key("userItem").begins_with("todo#")
        )

        items.extend(results["Items"])

    LOG.info("fixing up retrieved item(s) for client.")

    for item in items:
        item["todoId"] = item["userItem"][5:]
        item.pop("userItem")
        item.pop("userId")

    LOG.info("successfully retrieved item(s).")

    return make_response(context.aws_request_id, body={"result": items})
