from dataclasses import field

from boto3.dynamodb.conditions import Key
from marshmallow_dataclass import dataclass

from api import errorcodes
from api.dynamodb import TABLE, get_todo, user_exists
from api.log import get_logger
from api.response import make_response
from api.types import BaseRequest

LOG = get_logger()


@dataclass
class DeletePathParams(BaseRequest):
    user_id: str = field(metadata={"data_key": "userId"})
    todo_id: str = field(metadata={"data_key": "todoId"})


def handle(event, context):
    """Deletes todo item."""
    path_params = DeletePathParams.load(event["pathParameters"])

    LOG.info(f'deleting todo with id "{path_params.todo_id}" for username "{path_params.user_id}"')

    if not user_exists(path_params.user_id):
        LOG.error(f'username "{path_params.user_id}" does not exist.')
        return make_response(context.aws_request_id, 400, body={"error": errorcodes.RESOURCE_NOT_EXIST, "developerText": "user does not exist."})

    delete_request = {
        "userId": path_params.user_id,
        "userItem": f"todo#{path_params.todo_id}"
    }

    TABLE.delete_item(Key=delete_request)

    LOG.info(f'successfully deleted todo "{path_params.todo_id}".')

    return make_response(context.aws_request_id, 204)
