from functools import wraps

from src import errorcodes
from src.dynamodb import user_exists
from src.log import get_logger
from src.response import make_response

LOG = get_logger()


def require_user(f):
    @wraps(f)
    def wrapper(event, context):
        user_id = event["pathParameters"].get("userId")

        if not user_exists(user_id):
            LOG.error(f'user-id "{user_id}" does not exist.')
            return make_response(
                context.aws_request_id,
                400,
                error=errorcodes.RESOURCE_NOT_EXIST,
            )

        return f(event, context)

    return wrapper


def require_user_own_record(f):
    @wraps(f)
    def wrapper(event, context):
        body = event["body"] or {}

        requested_user_id = event["pathParameters"].get("userId") or body.get("userId")
        if requested_user_id is None:
            raise ValueError("userId not found in request path or body")

        authorizer_context = event["requestContext"].get("authorizer", {})

        authed_user_id = authorizer_context.get("userId")
        if authed_user_id is None:
            LOG.warn(f'unable to get authorized user-id for requested user-id "{requested_user_id}"')
        else:
            if requested_user_id != authed_user_id:
                LOG.error(
                    f'user-id "{authed_user_id}" requested access to data owned by "{requested_user_id}"; blocked'
                )
                return make_response(
                    context.aws_request_id,
                    403,
                    error=errorcodes.RESOURCE_NOT_OWNED_BY_REQUESTOR,
                )

        return f(event, context)

    return wrapper
