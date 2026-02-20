from database_dimension import DataModelHandler
from .payout_method import PayoutMethod

class PayoutMethodDataModelHandler(DataModelHandler, db="wallet_related_data", collection="payout_methods", model=PayoutMethod):
    @classmethod
    async def get_user_methods(cls, user_id: str) -> list[PayoutMethod]:
        return await cls.find({"user_id": user_id})

    @classmethod
    async def add_method(cls, user_id: str, type: str, provider_token: str, last4: str, brand: str = None) -> PayoutMethod:
        method = PayoutMethod(
            user_id=user_id,
            type=type,
            provider_token=provider_token,
            last4=last4,
            brand=brand
        )
        await cls.insert_one(method)
        return method
