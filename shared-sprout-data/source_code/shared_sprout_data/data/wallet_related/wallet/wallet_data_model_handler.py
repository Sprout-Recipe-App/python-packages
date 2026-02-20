from database_dimension import DataModelHandler
from .wallet import Wallet

class WalletDataModelHandler(DataModelHandler, db="wallet_related_data", collection="wallets", model=Wallet):
    @classmethod
    def user_query(cls, user_id: str) -> dict:
        return {"user_id": user_id}

    @classmethod
    async def find_by_user_id(cls, user_id: str) -> Wallet | None:
        return await cls.find_one(cls.user_query(user_id))

    @classmethod
    async def create_wallet_if_not_exists(cls, user_id: str) -> Wallet:
        existing = await cls.find_by_user_id(user_id)
        if existing:
            return existing
        
        new_wallet = Wallet(user_id=user_id)
        await cls.insert_one(new_wallet)
        return new_wallet

    @classmethod
    async def update_balance(cls, user_id: str, amount: float):
        # Using $inc for atomic update
        await cls.update_one(cls.user_query(user_id), {"$inc": {"available_balance": amount}})
