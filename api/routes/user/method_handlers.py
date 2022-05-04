import logging
from dataclasses import field

from marshmallow_dataclass import dataclass

from api import errorcodes
from api.dynamodb import create_user, user_exists
from api.log import get_logger
from api.response import make_response
from api.types import BaseRequest

LOG = get_logger()


@dataclass
class CreateRequest(BaseRequest):
    user_id: str = field(metadata={"data_key": "username"})


def create(event, context):
    """Creates userId:<user-id> userItem:config attributes:{categories: []}."""
    request = CreateRequest.loads(event["body"])

    LOG.info(f'user create request with username: {request.user_id}')

    if user_exists(request.user_id):
        LOG.error(f'username "{request.user_id}" already exists')
        return make_response(context.aws_request_id, 400, body={"error": errorcodes.RESOURCE_ALREADY_EXIST, "developerText": ""})

    create_user(request.user_id)

    LOG.info(f'Created user {request.user_id}')

    return make_response(context.aws_request_id, 201, body={"username": request.user_id})


METHOD_HANDLERS = {
    "POST": create,
}