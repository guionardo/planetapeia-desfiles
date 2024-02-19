from datetime import timedelta
from time import time


class MemCache:
    def __init__(self, default_ttl: timedelta = timedelta(seconds=30)):
        self.default_ttl = default_ttl
        self.items = {}

    def set(self, key, value):
        self.items[key] = (value, time() + self.default_ttl.total_seconds())

    def get(self, key, default_value=None):
        if value := self.items.get(key):
            if value[1] > time():
                return value[0]
            del self.items[key]

        return default_value
