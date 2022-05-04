import uuid
from dataclasses import field
from typing import Optional

from marshmallow_dataclass import dataclass

from api import errorcodes
from api.dynamodb import TABLE, user_exists
from api.log import get_logger
from api.response import make_response
from api.types import BaseRequest

LOG = get_logger()


@dataclass
class CreateRequest(BaseRequest):
    body: str
    category: Optional[str] = field(default="")
    completed: Optional[bool] = field(default=False)
    deleted: Optional[bool] = field(default=False)


def handle(event, context):
    """Creates userId:<user-id> userItem:todo#<todoId> attributes:{body: <text>}."""
    request = CreateRequest.validates(event["body"])

    user_id = event["pathParameters"]["userId"]

    if not user_exists(user_id):
        LOG.error(f'username "{user_id}" does not exist.')
        return make_response(context.aws_request_id, 400, body={"error": errorcodes.RESOURCE_NOT_EXIST, "developerText": ""})

    request["userId"] = user_id

    todo_id = uuid.uuid4().hex
    request["userItem"] = f"todo#{todo_id}"

    TABLE.put_item(Item=request)

    LOG.info(f'Successfully created todo with id "{todo_id}".')

    return make_response(context.aws_request_id, 201, body={"todoId": todo_id})
