import logging
from dataclasses import field
from typing import Optional

from marshmallow import INCLUDE
from marshmallow_dataclass import dataclass

from api import errorcodes
from api.dynamodb import TABLE, create_user, user_exists
from api.log import get_logger
from api.response import make_response

LOG = get_logger()


@dataclass
class CreateRequest:
    class Meta:
        unknown = INCLUDE

    username: str
 
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
    """Creates userId:<user-id> userItem:config attributes:{categories: []}."""
    request = CreateRequest.validates(event["body"])

    user_id = request["username"]

    LOG.info(f'user create request with username: {user_id}')

    if user_exists(user_id):
        LOG.error(f'username "{user_id}" already exists')
        return make_response(context.aws_request_id, 400, body={"error": RESOURCE_ALREADY_EXIST, "developerText": ""})

    create_user(user_id)

    LOG.info(f'Created user {user_id}')

    return make_response(context.aws_request_id, 201, body={"userId": request["username"]})
