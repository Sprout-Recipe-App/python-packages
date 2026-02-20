from typing import Optional
from database_dimension import MongoDBBaseModel

from .supports.user_account import UserAccount
from .supports.user_identity import UserIdentity
from .supports.user_preferences.user_preferences import UserPreferences


class User(MongoDBBaseModel):
    account: UserAccount
    identity: UserIdentity
    preferences: UserPreferences
    email: Optional[str] = None
