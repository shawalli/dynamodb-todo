import os

import boto3

region = os.environ.get("AWS_REGION", "us-east-1")
endpoint = os.environ.get("LOCALSTACK_ENDPOINT", None)

DYNAMODB = boto3.resource("dynamodb", region_name=region, endpoint_url=endpoint)

TABLE = DYNAMODB.Table("todoServerless")
