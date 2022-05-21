from copy import deepcopy

import requests
from cachecontrol import CacheControl
from google.auth.transport.requests import Request as GoogleAuthRequest
from google.oauth2 import id_token

from src.constants import API_GATEWAY_RESOURCE_ARN, GOOGLE_OAUTH_CLIENT_ID
from src.log import get_logger
from src.types import BaseRequest

LOG = get_logger()


class AuthorizerPolicy:
    def __init__(self, principal_id, resource):
        self.principal_id = principal_id
        self.resource = resource
        self.context = {}

    def add_context(self, key, value):
        self.context[key] = value

    def build(self):
        policy = {
            "principalId": self.principal_id,
            "policyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Action": "execute-api:Invoke",
                        "Effect": "Allow",
                        "Resource": self.resource,
                    },
                ],
            },
        }

        if self.context:
            policy["context"] = deepcopy(self.context)

        return policy


def handle(event, context):
    """Validates request session tokens."""
    LOG.info(event)

    # get Authorization header
    LOG.info(f'auth header: {event["headers"]["Authorization"]}')
    auth_parts = event["headers"]["Authorization"].split(' ')
    if (len(auth_parts) != 2) or (auth_parts[0] != "Bearer"):
        raise Exception("Invalid Authorization header")

    token = auth_parts[1]

    # Validate token against Google public key
    session = requests.session()
    cached_session = CacheControl(session)
    request = GoogleAuthRequest(session=cached_session)

    id_info = id_token.verify_oauth2_token(token, request, GOOGLE_OAUTH_CLIENT_ID)
    principal_id = id_info['email']
    LOG.info(f'id_info: {id_info}')
    LOG.info(f'userID: {principal_id}')

    # Create policy and return it
    policy = AuthorizerPolicy(principal_id, API_GATEWAY_RESOURCE_ARN)
    policy.add_context("userId", principal_id)

    return policy.build()