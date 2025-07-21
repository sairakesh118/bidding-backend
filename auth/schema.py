from pydantic import BaseModel

class LoginRequest(BaseModel):
    email:str
    password: str
class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    email: str
    full_name: str
    owned_items: list = []
class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
class RegisterResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    email: str
    full_name: str
    owned_items: list = []
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    email: str
    is_active: bool
    is_superuser: bool
