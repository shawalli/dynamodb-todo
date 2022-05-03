import uuid

from boto3.dynamodb.conditions import Key

from api.dynamodb import TABLE, user_exists
from api.errorcodes import RESOURCE_NOT_EXIST
from api.log import get_logger
from api.response import make_response

LOG = get_logger()


def handle(event, context):
    """Gets one todo if todo-id given, else all user todos."""
    user_id = event["pathParameters"]["userId"]
    todo_id = event["pathParameters"].get("todoId")

    LOG.info(f'getting todo resource(s) for username "{user_id}"')

    if not user_exists(user_id):
        LOG.error(f'username "{user_id}" does not exist.')
        return make_response(context.aws_request_id, 400, body={"error": RESOURCE_NOT_EXIST, "developerText": ""})

    items = []
    if todo_id is not None:
        LOG.info(f'getting todo with id "{todo_id}"')
        todo_request = {
            "userId": user_id,
            "userItem": f"todo#{todo_id}",
        }

        results = TABLE.get_item(Key=todo_request)
        if "Item" in results:
            items.append(results["Item"])
        else:
            LOG.error(f'todo with id "{todo_id}" does not exist.')
            return make_response(context.aws_request_id, 404, body={"error": RESOURCE_NOT_EXIST, "developerText": ""})

    else:
        LOG.info("getting all todos for username")
        results = TABLE.query(
            KeyConditionExpression=Key("userId").eq(user_id) & Key("userItem").begins_with("todo#")
        )

        items.extend(results["Items"])

    LOG.info("fixing up retrieved item(s) for client.")

    for item in items:
        item["todo_id"] = item["userItem"][5:]
        item.pop("userItem")
        item.pop("userId")

    LOG.info("successfully retrieved item(s).")

    return make_response(context.aws_request_id, body={"result": items})
