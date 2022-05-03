from dataclasses import field
from typing import Optional

from marshmallow_dataclass import dataclass

from api import errorcodes
from api.dynamodb import TABLE, get_todo, user_exists
from api.log import get_logger
from api.response import make_response
from api.types import BaseRequest

LOG = get_logger()

@dataclass
class UpdateRequest(BaseRequest):
    body: str
    category: Optional[str] = field(default="")
    completed: Optional[bool] = field(default=False)
    deleted: Optional[bool] = field(default=False)


@dataclass
class UpdatePathParams(BaseRequest):
    user_id: str = field(metadata={"data_key": "userId"})
    todo_id: str = field(metadata={"data_key": "todoId"})


def handle(event, context):
    """Creates userId:<user-id> userItem:todo#<todoId> attributes:{body: <text>}."""
    request = UpdateRequest.validates(event["body"])

    path_params = UpdatePathParams.load(event["pathParameters"])

    LOG.info(f'deleting todo with id "{path_params.todo_id}" for username "{path_params.user_id}"')

    if not user_exists(path_params.user_id):
        LOG.error(f'username "{path_params.user_id}" does not exist.')
        return make_response(context.aws_request_id, 400, body={"error": errorcodes.RESOURCE_NOT_EXIST, "developerText": "user does not exist."})

    if get_todo(path_params.user_id, path_params.todo_id) is None:
        LOG.error(f'todo "{path_params.todo_id}" does not exist.')
        return make_response(context.aws_request_id, 404, body={"error": errorcodes.RESOURCE_NOT_EXIST, "developerText": ""})

    request["userId"] = path_params.user_id
    request["userItem"] = f"todo#{path_params.todo_id}"

    TABLE.put_item(Item=request)

    LOG.info(f'Successfully created todo with id "{path_params.todo_id}".')

    return make_response(context.aws_request_id, 204)
