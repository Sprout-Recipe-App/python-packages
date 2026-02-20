from pydantic import BaseModel


class GUIPreferences(BaseModel):
    background_images_enabled: bool = True
    glass_effects_enabled: bool = True
