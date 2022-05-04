import uuid
from dataclasses import field
from typing import Optional

from boto3.dynamodb.conditions import Key
from marshmallow_dataclass import dataclass

from api import errorcodes
from api.dynamodb import TABLE, get_todo, user_exists
from api.log import get_logger
from api.response import make_response
from api.types import BaseRequest

LOG = get_logger()


@dataclass
class CreateUpdateRequest(BaseRequest):
    body: str
    category: Optional[str] = field(default="")
    completed: Optional[bool] = field(default=False)
    deleted: Optional[bool] = field(default=False)


@dataclass
class CreatePathParams(BaseRequest):
    user_id: str = field(metadata={"data_key": "userId"})


def create(event, context):
    """Creates userId:<user-id> userItem:todo#<todoId> attributes:{body: <text>}."""
    request = CreateUpdateRequest.validates(event["body"])

    path_params = GetPathParams.load(event["pathParameters"])

    if not user_exists(path_params.user_id):
        LOG.error(f'username "{path_params.user_id}" does not exist.')
        return make_response(
            context.aws_request_id,
            400,
            body={"error": errorcodes.RESOURCE_NOT_EXIST, "developerText": ""},
        )

    request["userId"] = path_params.user_id

    todo_id = uuid.uuid4().hex
    request["userItem"] = f"todo#{todo_id}"

    TABLE.put_item(Item=request)

    LOG.info(f'Successfully created todo with id "{todo_id}".')

    return make_response(context.aws_request_id, 201, body={"todoId": todo_id})


@dataclass
class GetPathParams(BaseRequest):
    user_id: str = field(metadata={"data_key": "userId"})
    todo_id: Optional[str] = field(metadata={"data_key": "todoId"})


def get(event, context):
    """Gets one todo if todo-id given, else all user todos."""

    path_params = GetPathParams.load(event["pathParameters"])

    LOG.info(f'getting todo resource(s) for username "{path_params.user_id}"')

    if not user_exists(path_params.user_id):
        LOG.error(f'username "{path_params.user_id}" does not exist.')
        return make_response(context.aws_request_id, 400, body={"error": errorcodes.RESOURCE_NOT_EXIST, "developerText": ""})

    items = []
    if path_params.todo_id is not None:
        LOG.info(f'getting todo with id "{path_params.todo_id}"')
        todo_request = {
            "userId": path_params.user_id,
            "userItem": f"todo#{path_params.todo_id}",
        }

        results = TABLE.get_item(Key=todo_request)
        if "Item" in results:
            items.append(results["Item"])
        else:
            LOG.error(f'todo with id "{path_params.todo_id}" does not exist.')
            return make_response(context.aws_request_id, 404, body={"error": errorcodes.RESOURCE_NOT_EXIST, "developerText": ""})

    else:
        LOG.info("getting all todos for username")
        results = TABLE.query(
            KeyConditionExpression=Key("userId").eq(path_params.user_id) & Key("userItem").begins_with("todo#")
        )

        items.extend(results["Items"])

    LOG.info("fixing up retrieved item(s) for client.")

    for item in items:
        item["todoId"] = item["userItem"][5:]
        item.pop("userItem")
        item.pop("userId")

    LOG.info("successfully retrieved item(s).")

    return make_response(context.aws_request_id, body={"result": items})


@dataclass
class UpdatePathParams(BaseRequest):
    user_id: str = field(metadata={"data_key": "userId"})
    todo_id: str = field(metadata={"data_key": "todoId"})


def update(event, context):
    """Updates userId:<user-id> userItem:todo#<todoId>."""
    request = CreateUpdateRequest.validates(event["body"])

    path_params = UpdatePathParams.load(event["pathParameters"])

    LOG.info(f'updating todo with id "{path_params.todo_id}" for username "{path_params.user_id}"')

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


@dataclass
class DeletePathParams(BaseRequest):
    user_id: str = field(metadata={"data_key": "userId"})
    todo_id: str = field(metadata={"data_key": "todoId"})


def delete(event, context):
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


METHOD_HANDLERS = {
    "GET": get,
    "POST": create,
    "PUT": update,
    "DELETE": delete,
}