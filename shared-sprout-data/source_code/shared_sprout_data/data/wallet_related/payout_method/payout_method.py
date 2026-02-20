from database_dimension import MongoDBBaseModel
from typing import Optional
from datetime import datetime

class PayoutMethod(MongoDBBaseModel):
    user_id: str
    type: str  # "BANK_ACCOUNT", "DEBIT_CARD"
    provider_token: str  # Stripe token / bank account token
    last4: str
    brand: Optional[str] = None  # Visa, Chase, etc.
    is_default: bool = False
    created_at: datetime = datetime.utcnow()
