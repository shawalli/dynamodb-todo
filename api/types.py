from marshmallow_dataclass import dataclass
from marshmallow import INCLUDE


@dataclass
class BaseRequest:
    class Meta:
        unknown = INCLUDE

    @classmethod
    def load(cls, obj):
        return cls.Schema().load(obj)

    @classmethod
    def loads(cls, obj):
        return cls.Schema().loads(obj)

    @classmethod
    def dump(cls, obj):
        return cls.Schema().dump(obj)

    @classmethod
    def validate(cls, obj):
        return cls.dump(cls.load(obj))

    @classmethod
    def validates(cls, obj):
        return cls.dump(cls.loads(obj))

