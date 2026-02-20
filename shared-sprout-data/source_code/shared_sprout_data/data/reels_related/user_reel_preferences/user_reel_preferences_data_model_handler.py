from collections import defaultdict
from datetime import datetime, timezone
from database_dimension import MongoDBBaseModel, DataModelHandler
from pydantic import Field

class OnboardingAnswers(MongoDBBaseModel):
    content_interests: list[str] = []
    viewer_type: str | None = None
    dietary_preferences: list[str] = []
    complexity_preference: str | None = None
    taste_profiles: list[str] = []

class UserReelPreferences(MongoDBBaseModel):
    user_id: str
    
    onboarding_answers: OnboardingAnswers | None = None
    
    interest_vector: dict[str, float] = Field(default_factory=dict)
    
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserReelPreferencesDataModelHandler(DataModelHandler, db="reels_related_data", collection="user_reel_preferences", model=UserReelPreferences):
    @classmethod
    async def get_or_create(cls, user_id: str) -> UserReelPreferences:
        if prefs := await cls.find_one({"user_id": user_id}):
            return prefs
        
        new_prefs = UserReelPreferences(user_id=user_id)
        return new_prefs

    @classmethod
    async def save(cls, prefs: UserReelPreferences):
        await cls.replace_one({"user_id": prefs.user_id}, prefs, upsert=True)
