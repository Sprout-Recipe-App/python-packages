from pydantic import BaseModel

from .supports.gui_preferences import GUIPreferences
from .supports.recipe_preferences import RecipePreferences


class UserPreferences(BaseModel):
    priority: str | None = None
    recipe_preferences: RecipePreferences = RecipePreferences()
    gui_preferences: GUIPreferences = GUIPreferences()
    saved_recipe_ids: list[str] = []
    dismissed_recipe_ids: set[str] = set()
    blocked_user_ids: set[str] = set()
    last_meal_champion_recipe_id: str | None = None
