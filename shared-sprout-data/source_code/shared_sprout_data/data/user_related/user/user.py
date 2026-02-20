from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from database_dimension import MongoDBBaseModel

from ...shared.recipe_enumerations import DietType, RecipeComplexity


class UserAccount(BaseModel):
    user_id: str
    email: str | None = None


class UserIdentity(BaseModel):
    name: str
    birthday: datetime


class GUIPreferences(BaseModel):
    background_images_enabled: bool = False


class RecipePreferences(BaseModel):
    diet_type: DietType | None = None
    excluded_ingredients: list[str] = []
    max_complexity: RecipeComplexity | None = None
    default_instructions: str | None = None
    measurement_system: str = "US"


class UserPreferences(BaseModel):
    top_goals: list[str] = []
    recipe_preferences: RecipePreferences = RecipePreferences()
    gui_preferences: GUIPreferences = GUIPreferences()
    saved_recipe_ids: list[str] = []
    dismissed_recipe_ids: list[str] = []
    blocked_user_ids: list[str] = []


class User(MongoDBBaseModel, database="sprout_data", collection="users"):
    account: UserAccount
    identity: UserIdentity | None = None
    preferences: UserPreferences
    points: float = 0
