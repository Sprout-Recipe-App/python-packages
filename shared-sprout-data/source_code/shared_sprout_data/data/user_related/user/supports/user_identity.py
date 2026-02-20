from datetime import datetime

from pydantic import BaseModel


class UserIdentity(BaseModel):
    name: str
    birthday: datetime
