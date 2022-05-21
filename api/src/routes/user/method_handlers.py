import logging
from dataclasses import field

from marshmallow_dataclass import dataclass

from src import errorcodes
from src.decorators import require_user_own_record
from src.dynamodb import create_user, get_user_config, user_exists
from src.log import get_logger
from src.response import make_response
from src.types import BaseRequest

LOG = get_logger()


@dataclass
class GetPathParams(BaseRequest):
    user_id: str = field(metadata={"data_key": "userId"})


@require_user_own_record
def get(event, context):
    """Gets one todo if todo-id given, else all user todos."""

    path_params = GetPathParams.load(event["pathParameters"])

    LOG.info(f'getting user resource(s) for user-id "{path_params.user_id}"')

    user_config = get_user_config(path_params.user_id)

    if user_config is None:
        user_config = {}
        LOG.warn(f'No user found with user-id "{path_params.user_id}"')

    return make_response(context.aws_request_id, body={"result": user_config})


@dataclass
class CreateRequest(BaseRequest):
    user_id: str = field(metadata={"data_key": "userId"})


@require_user_own_record
def create(event, context):
    """Creates userId:<user-id> userItem:config attributes:{categories: []}."""
    request = CreateRequest.loads(event["body"])

    LOG.info(f'user create request with user-id: {request.user_id}')

    if user_exists(request.user_id):
        LOG.error(f'user-id "{request.user_id}" already exists')
        return make_response(context.aws_request_id, 400, errorcodes.RESOURCE_ALREADY_EXIST)

    create_user(request.user_id)

    LOG.info(f'Created user {request.user_id}')

    return make_response(context.aws_request_id, 201, body={"userId": request.user_id})


METHOD_HANDLERS = {
    "GET": get,
    "POST": create,
}