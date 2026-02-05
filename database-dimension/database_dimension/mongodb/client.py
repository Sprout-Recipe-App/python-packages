from functools import cache
from os import getenv

from pymongo import AsyncMongoClient


@cache
def get_mongodb_client():
    return AsyncMongoClient(
        f"mongodb+srv://{getenv('MONGODB_ATLAS_USERNAME')}:{getenv('MONGODB_ATLAS_PASSWORD')}@{getenv('MONGODB_ATLAS_CLUSTER_ADDRESS')}/?retryWrites=true&w=majority&appName={getenv('MONGODB_ATLAS_CLUSTER_NAME')}"
    )
