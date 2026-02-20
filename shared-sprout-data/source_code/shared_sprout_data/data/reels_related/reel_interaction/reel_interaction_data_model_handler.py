from datetime import datetime, timezone
from enum import Enum
from database_dimension import MongoDBBaseModel, DataModelHandler
from pydantic import Field

class InteractionType(str, Enum):
    IMPRESSION = "impression"
    VIEW = "view" 
    LIKE = "like"
    DISLIKE = "dislike"
    SAVE = "save"
    SHARE = "share"
    SKIP = "skip"
    COMPLETE = "complete"

class ReelInteraction(MongoDBBaseModel):
    user_id: str
    reel_id: str
    interaction_type: InteractionType
    
    watch_time_seconds: float = 0.0
    percentage_watched: float = 0.0
    
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ReelInteractionDataModelHandler(DataModelHandler, db="reels_related_data", collection="reel_interactions", model=ReelInteraction):
    pass
