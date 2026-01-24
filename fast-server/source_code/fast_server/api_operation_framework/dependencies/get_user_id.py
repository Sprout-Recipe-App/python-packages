from fastapi import Header


async def get_user_id(authorization: str = Header()) -> str:
    return authorization[7:].strip()

