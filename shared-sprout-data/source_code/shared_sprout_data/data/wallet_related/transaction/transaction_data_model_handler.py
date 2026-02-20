from datetime import datetime
from typing import Optional

from database_dimension import DataModelHandler

from .transaction import Transaction


class TransactionDataModelHandler(DataModelHandler, db="wallet_related_data", collection="transactions", model=Transaction):
    @classmethod
    async def find_by_payment_intent(cls, payment_intent_id: str) -> Transaction | None:
        return await cls.find_one({"reference_id": payment_intent_id})

    @classmethod
    async def find_by_user_paginated(
        cls,
        user_id: str,
        *,
        skip: int = 0,
        limit: int = 20,
        type_filter: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> tuple[list[Transaction], int]:
        """
        Fetch transactions for a user with filters and pagination.
        Returns (transactions, total_count).
        """
        query: dict = {"user_id": user_id}
        if type_filter:
            query["type"] = type_filter
        if start_date or end_date:
            date_query: dict = {}
            if start_date:
                date_query["$gte"] = start_date
            if end_date:
                date_query["$lte"] = end_date
            if date_query:
                query["created_at"] = date_query

        coll = cls.collection()
        total = await coll.count_documents(query)
        cursor = coll.find(query).sort("created_at", -1).skip(skip).limit(limit)
        docs = await cursor.to_list(limit)
        transactions = [cls._validate(d) for d in docs if cls._validate(d)]
        return transactions, total

    @classmethod
    async def create_deposit_transaction(cls, user_id: str, amount: float, payment_intent_id: str) -> Transaction:
        transaction = Transaction(
            user_id=user_id,
            amount=amount,
            type="DEPOSIT",
            status="PENDING",
            reference_id=payment_intent_id
        )
        await cls.insert_one(transaction)
        return transaction

    @classmethod
    async def mark_completed(cls, transaction_id: str):
        from datetime import datetime
        await cls.update_one(
            {"id": transaction_id}, 
            {"$set": {"status": "COMPLETED", "completed_at": datetime.utcnow()}}
        )
