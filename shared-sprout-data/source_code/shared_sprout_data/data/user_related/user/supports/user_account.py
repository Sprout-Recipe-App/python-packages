from pydantic import BaseModel


class UserAccount(BaseModel):
    user_id: str
    account_type: str
