from .schema import LoginRequest , TokenResponse
from core.security import create_access_token

async def login_user(data: LoginRequest):
    # Validate user, hash password, etc.
    token = create_access_token({"sub": data.email})
    return token
