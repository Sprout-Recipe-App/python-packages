from database_dimension import MongoDBBaseModel
from typing import Optional
from datetime import datetime

class Wallet(MongoDBBaseModel):
    user_id: str
    available_balance: float = 0.0
    pending_balance: float = 0.0
    bonus_balance: float = 0.0
    currency: str = "USD"
    stripe_customer_id: Optional[str] = None
    
    # Stripe Connect fields
    stripe_connected_account_id: Optional[str] = None
    connect_onboarding_completed: bool = False
    connect_charges_enabled: bool = False
    connect_payouts_enabled: bool = False
    connect_completed_at: Optional[datetime] = None
    oauth_state: Optional[str] = None  # Temporary storage for OAuth CSRF protection
