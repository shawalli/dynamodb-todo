from marshmallow_dataclass import dataclass
from marshmallow import INCLUDE


@dataclass
class BaseRequest:
    class Meta:
        unknown = INCLUDE

    @classmethod
    def loads(cls, obj):
        return cls.Schema().loads(obj)
    
    @classmethod
    def dump(cls, obj):
        return cls.Schema().dump(obj)
    
    @classmethod
    def validates(cls, obj):
        return cls.dump(cls.loads(obj))

