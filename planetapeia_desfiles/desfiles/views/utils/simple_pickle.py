import datetime
import json

from dateutil.parser import ParserError, parse
from django.core.serializers.json import DjangoJSONEncoder


def object_hook(obj: dict):
    for key, value in obj.items():
        if isinstance(value, str):
            try:
                obj[key] = parse(value)
            except ParserError:
                pass

    return obj


def loads(dump: str):
    return json.loads(dump, object_hook=object_hook)


def dumps(data: dict) -> str:
    return json.dumps(data, cls=DjangoJSONEncoder)


if __name__ == "__main__":
    sample = {"name": "Guionardo", "date": datetime.datetime(2024, 3, 7, 10, 10, 10)}
    as_json = dumps(sample)
    print(as_json)

    sample_copy = loads(as_json)
    assert sample["name"] == sample_copy["name"]
    assert sample["date"] == sample_copy["date"]
