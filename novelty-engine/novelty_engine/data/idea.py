from datetime import datetime

from database_dimension import MongoDBBaseModel
from pydantic import Field


class Idea(MongoDBBaseModel):
    content: str
    user_id: str | None = Field(default=None, serialization_alias="userId", validation_alias="userId")
    created_at: datetime = Field(default_factory=datetime.now)
    processed_at: datetime | None = Field(default=None, exclude=True)

