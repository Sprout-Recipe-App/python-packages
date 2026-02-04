from contextvars import ContextVar
from datetime import timezone
from os import getenv

from bson.codec_options import CodecOptions
from pymongo import AsyncMongoClient


class DatabaseGateway:
    _codec = CodecOptions(tz_aware=True, tzinfo=timezone.utc)
    _instance: ContextVar["DatabaseGateway | None"] = ContextVar("gw", default=None)

    def __init__(self):
        def env(k):
            return getenv(f"MONGODB_ATLAS_{k}")

        self._client = AsyncMongoClient(
            f"mongodb+srv://{env('USERNAME')}:{env('PASSWORD')}@{env('CLUSTER_ADDRESS')}/?retryWrites=true&w=majority&appName={env('CLUSTER_NAME')}"
        )

    def get_collection(self, m):
        return self._client[m._db_name].get_collection(m._collection_name, codec_options=self._codec)

    @classmethod
    def get(cls):
        if not (gw := cls._instance.get()):
            cls._instance.set(gw := cls())
        return gw
