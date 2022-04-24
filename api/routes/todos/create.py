import uuid
from dataclasses import field
from typing import Optional

from marshmallow import INCLUDE
from marshmallow_dataclass import dataclass

from api.dynamodb import TABLE, user_exists
from api.errorcodes import RESOURCE_NOT_EXIST
from api.log import get_logger
from api.response import make_response

LOG = get_logger()

@dataclass
class CreateRequest:
    class Meta:
        unknown = INCLUDE

    body: str
    category: Optional[str] = field(default="")

    @classmethod
    def loads(cls, obj):
        return cls.Schema().loads(obj)
    
    @classmethod
    def dump(cls, obj):
        return cls.Schema().dump(obj)
    
    @classmethod
    def validates(cls, obj):
        return cls.dump(cls.loads(obj))


def handle(event, context):
    """Creates userId:<user-id> userItem:todo#<todoId> attributes:{body: <text>}."""
    request = CreateRequest.validates(event["body"])

    user_id = event["pathParameters"]["userId"]

    if not user_exists(user_id):
        LOG.error(f'username "{user_id}" does not exist.')
        return make_response(context.aws_request_id, 400, body={"error": RESOURCE_NOT_EXIST, "developerText": ""})

    request["userId"] = user_id

    todo_id = uuid.uuid4().hex
    request["userItem"] = f"todo#{todo_id}"

    TABLE.put_item(Item=request)

    LOG.info(f'Successfully created todo with id "{todo_id}".')

    return make_response(context.aws_request_id, 201, body={"todoId": todo_id})
