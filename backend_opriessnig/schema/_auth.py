from pydantic import BaseModel, Field


class UserRegister(BaseModel):
    user_name: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)
    name: str = Field(min_length=1, max_length=255)


class UserLogin(BaseModel):
    user_name: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_name: str
    user_id: int
