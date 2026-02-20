from datetime import datetime, timezone
from database_dimension import MongoDBBaseModel
from pydantic import Field

class ReelStats(MongoDBBaseModel):
    views: int = 0
    likes: int = 0
    shares: int = 0
    saves: int = 0
    completion_rate: float = 0.0
    avg_watch_time: float = 0.0

class Reel(MongoDBBaseModel):
    creator_id: str
    video_url: str
    thumbnail_url: str
    description: str | None = None
    duration_seconds: int
    aspect_ratio: str = "9:16"
    
    tags: list[str] = []
    
    dish_type: str | None = None
    cuisine: str | None = None
    dietary_tags: list[str] = []
    flavor_profile: list[str] = []
    difficulty: str | None = None
    
    stats: ReelStats = Field(default_factory=ReelStats)
    
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ReelDataModelHandler:
    pass
