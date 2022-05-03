import uuid

from boto3.dynamodb.conditions import Key

from api import errorcodes
from api.dynamodb import TABLE, get_todo, user_exists
from api.log import get_logger
from api.response import make_response

LOG = get_logger()


def handle(event, context):
    """Deletes todo item."""
    user_id = event["pathParameters"]["userId"]
    todo_id = event["pathParameters"]["todoId"]
    LOG.info(f'deleting todo with id "{todo_id}" for username "{user_id}"')

    if not user_exists(user_id):
        LOG.error(f'username "{user_id}" does not exist.')
        return make_response(context.aws_request_id, 400, body={"error": errorcodes.RESOURCE_NOT_EXIST, "developerText": "user does not exist."})

    delete_request = {
        "userId": user_id,
        "userItem": f"todo#{todo_id}"
    }

    TABLE.delete_item(Key=delete_request)

    LOG.info(f'successfully deleted todo "{todo_id}".')

    return make_response(context.aws_request_id)
