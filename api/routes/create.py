import json
from dataclasses import field
from typing import Optional

from marshmallow import INCLUDE
from marshmallow_dataclass import dataclass

@dataclass
class CreateRequest:
    class Meta:
        unknown = INCLUDE

    user_id: str = field(metadata=dict(data_key="userId"))
    body: str
    category: Optional[str]

    @classmethod
    def loads(cls, obj):
        return cls.Schema().loads(obj)

def handle(event, context):
    print(event["body"])
    request = CreateRequest.loads(event["body"])
    print(request)
