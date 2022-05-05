from src.log import get_logger
from src.response import make_response
from src.routes.todos.method_handlers import METHOD_HANDLERS

LOG = get_logger()


def handle(event, context):
    """Handles todo resource requests."""

    method = event["httpMethod"]
    LOG.info(f"received todo resource {method} request")

    resolved_handler = METHOD_HANDLERS.get(method)

    if resolved_handler is None:
        LOG.error(f"todo resource {method} method not allowed")
        return make_response(context.aws_request_id, 405)

    return resolved_handler(event, context)
