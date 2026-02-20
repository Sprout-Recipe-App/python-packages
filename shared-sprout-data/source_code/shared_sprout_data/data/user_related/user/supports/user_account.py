from pydantic import BaseModel


class UserAccount(BaseModel):
    user_id: str
    email: str | None = None
