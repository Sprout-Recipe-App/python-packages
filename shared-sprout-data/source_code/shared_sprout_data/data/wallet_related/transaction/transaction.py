from database_dimension import MongoDBBaseModel
from typing import Optional
from datetime import datetime

class Transaction(MongoDBBaseModel):
    user_id: str
    amount: float
    currency: str = "USD"
    type: str  # DEPOSIT
    status: str  # PENDING, COMPLETED, FAILED
    reference_id: Optional[str] = None  # Stripe Payment Intent ID
    metadata: Optional[dict] = None
    created_at: datetime = datetime.utcnow()
    completed_at: Optional[datetime] = None
