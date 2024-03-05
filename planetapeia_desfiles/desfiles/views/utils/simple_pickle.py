import json

from bson import json_util
from django.core.serializers.json import DjangoJSONEncoder


def loads(dump: str):
    return json.loads(dump, object_hook=json_util.object_hook)


def dumps(data: dict) -> str:
    return json.dumps(data, cls=DjangoJSONEncoder)
