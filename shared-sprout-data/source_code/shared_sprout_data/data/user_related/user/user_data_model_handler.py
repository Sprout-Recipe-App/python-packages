from datetime import datetime, timezone


from .user import User, UserAccount, UserIdentity, UserPreferences


class UserDataModelHandler:
    @classmethod
    def user_query(cls, user_id: str) -> dict:
        return {"account.user_id": user_id}

    @classmethod
    async def find_by_user_id(cls, user_id: str) -> User | None:
        return await cls.find_one(cls.user_query(user_id))

    @classmethod
    async def add_saved_recipe(cls, user_id: str, recipe_id: str) -> None:
        await cls.update_one(cls.user_query(user_id), {"$addToSet": {"preferences.saved_recipe_ids": recipe_id}})

    @staticmethod
    def _preview_user(
        user_id: str,
        name: str,
        birthday: datetime,
        priority: str = "Improving Health",
    ) -> User:
        return User(
            account=UserAccount(user_id=user_id),
            identity=UserIdentity(name=name, birthday=birthday),
            preferences=UserPreferences(priority=priority),
        )

    SEED_DATA = [
        _preview_user("preview-user-alice", "Alice", datetime(1990, 6, 15, tzinfo=timezone.utc)),
        _preview_user("preview-user-bob", "Bob", datetime(1985, 3, 22, tzinfo=timezone.utc)),
        _preview_user("preview-user-free", "Free User", datetime(2000, 1, 1, tzinfo=timezone.utc)),
    ]
