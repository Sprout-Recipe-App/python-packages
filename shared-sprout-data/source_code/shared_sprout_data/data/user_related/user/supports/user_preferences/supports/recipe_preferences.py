from pydantic import BaseModel

from ......shared.recipe_enumerations import DietType, RecipeComplexity


class RecipePreferences(BaseModel):
    diet_type: DietType = DietType.ANY
    excluded_ingredients: list[str] = []
    max_complexity: RecipeComplexity | None = None
    excluded_equipment: list[str] = []
    max_cooking_time: int | None = None
    default_instructions: str | None = None
    measurement_system: str = "US"
