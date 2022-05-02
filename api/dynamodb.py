import os

import boto3

region = os.environ.get("AWS_REGION", "us-east-1")

DYNAMODB = boto3.resource("dynamodb", region_name=region)

TABLE = DYNAMODB.Table("todoServerless")


def get_user_config(user_id):
    user_config = {
        "userId": user_id,
        "userItem": "config",
    }

    results = TABLE.get_item(Key=user_config)

    if "Item" not in results:
        return None
    
    return results["Item"]


def user_exists(user_id):
    return get_user_config(user_id) is not None


def create_user(user_id, **user_settings):
    if "categories" not in user_settings:
        user_settings["categories"] = []

    item = dict(userId=user_id, userItem="config", **user_settings)

    TABLE.put_item(Item=item)
