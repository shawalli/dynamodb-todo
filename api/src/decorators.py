import logging
from dataclasses import field
from functools import wraps

from marshmallow import EXCLUDE
from marshmallow_dataclass import dataclass

from src import errorcodes
from src.dynamodb import create_user, user_exists
from src.log import get_logger
from src.response import make_response
from src.types import BaseRequest

LOG = get_logger()


@dataclass
class HandlerUserRequiredPathParams(BaseRequest):
    class Meta:
        unknown = EXCLUDE

    user_id: str = field(metadata={"data_key": "userId"})


def handler_user_required(f):
    @wraps(f)
    def wrapper(event, context):
        path_params = HandlerUserRequiredPathParams.load(event["pathParameters"])

        if not user_exists(path_params.user_id):
            LOG.error(f'username "{path_params.user_id}" does not exist.')
            return make_response(
                context.aws_request_id,
                400,
                body={"error": errorcodes.RESOURCE_NOT_EXIST, "developerText": ""},
            )
        
        return f(event, context)
    
    return wrapper

def handler_todo_required(f):
    @wraps(f)
    def wrapper(event, context):
        path_params = HandlerUserRequiredPathParams.load(event["pathParameters"])

        if not todo_exists(path_params.user_id, path_params.todo_id):
            LOG.error(f'username "{path_params.user_id}" does not exist.')
            return make_response(
                context.aws_request_id,
                400,
                body={"error": errorcodes.RESOURCE_NOT_EXIST, "developerText": ""},
            )
        
        return f(event, context)
    
    return wrapper