from api.log import get_logger
from api.response import make_response
from api.routes.user.method_handlers import METHOD_HANDLERS

LOG = get_logger()


def handle(event, context):
    """Handles user resource requests."""

    method = event["httpMethod"]
    LOG.info(f"received user resource {method} request")

    resolved_handler = METHOD_HANDLERS.get(method)

    if resolved_handler is None:
        LOG.error(f"user resource {method} method not allowed")
        return make_response(context.aws_request_id, 405)

    return resolved_handler(event, context)
