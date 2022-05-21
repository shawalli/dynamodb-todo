import uuid
from dataclasses import field
from typing import Optional

from boto3.dynamodb.conditions import Key
from marshmallow_dataclass import dataclass

from src import errorcodes
from src.decorators import require_user, require_user_own_record
from src.dynamodb import TABLE, get_todo, user_exists
from src.log import get_logger
from src.response import make_response
from src.types import BaseRequest

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


@require_user
@require_user_own_record
def create(event, context):
    """Creates userId:<user-id> userItem:todo#<todoId> attributes:{body: <text>}."""
    request = CreateUpdateRequest.validates(event["body"])

    path_params = GetPathParams.load(event["pathParameters"])

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


@require_user
@require_user_own_record
def get(event, context):
    """Gets one todo if todo-id given, else all user todos."""

    path_params = GetPathParams.load(event["pathParameters"])

    LOG.info(f'getting todo resource(s) for user-id "{path_params.user_id}"')

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
            return make_response(context.aws_request_id, 404, error=errorcodes.RESOURCE_NOT_EXIST)

    else:
        LOG.info("getting all todos for user-id")
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


@require_user
@require_user_own_record
def update(event, context):
    """Updates userId:<user-id> userItem:todo#<todoId>."""
    request = CreateUpdateRequest.validates(event["body"])

    path_params = UpdatePathParams.load(event["pathParameters"])

    LOG.info(f'updating todo with id "{path_params.todo_id}" for user-id "{path_params.user_id}"')

    if get_todo(path_params.user_id, path_params.todo_id) is None:
        LOG.error(f'todo "{path_params.todo_id}" does not exist.')
        return make_response(context.aws_request_id, 404, error=errorcodes.RESOURCE_NOT_EXIST)

    request["userId"] = path_params.user_id
    request["userItem"] = f"todo#{path_params.todo_id}"

    TABLE.put_item(Item=request)

    LOG.info(f'Successfully created todo with id "{path_params.todo_id}".')

    return make_response(context.aws_request_id, 204)


@dataclass
class DeletePathParams(BaseRequest):
    user_id: str = field(metadata={"data_key": "userId"})
    todo_id: str = field(metadata={"data_key": "todoId"})


@require_user
@require_user_own_record
def delete(event, context):
    """Deletes todo item."""
    path_params = DeletePathParams.load(event["pathParameters"])

    LOG.info(f'deleting todo with id "{path_params.todo_id}" for user-id "{path_params.user_id}"')

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