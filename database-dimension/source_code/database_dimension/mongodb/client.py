from datetime import timezone
import os

from bson.codec_options import CodecOptions
from motor.motor_asyncio import AsyncIOMotorClient


class MongoDBClient:
    _codec_opts = CodecOptions(tz_aware=True, tzinfo=timezone.utc)

    def __init__(self):
        env = os.getenv
        self._client = AsyncIOMotorClient(
            f"mongodb+srv://{env('MONGODB_ATLAS_USERNAME')}:{env('MONGODB_ATLAS_PASSWORD')}@{env('MONGODB_ATLAS_CLUSTER_ADDRESS')}/?retryWrites=true&w=majority&appName={env('MONGODB_ATLAS_CLUSTER_NAME')}"
        )

    def get_collection(self, database_name, collection_name):
        return self._client[database_name].get_collection(collection_name, codec_options=self._codec_opts)

    def close(self):
        self._client.close()

