from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class CartItemRequest(BaseModel):
    frame_id: str
    quantity: int = Field(default=1, ge=1, le=10)


class CartQuantityRequest(BaseModel):
    quantity: int = Field(ge=1, le=10)
