from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, ExpiredSignatureError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel


class TokenData(BaseModel):
    user_name: str
    user_id: Optional[int] = None


class AuthService:
    """Service for authentication and token management"""
    
    # Configuration
    SECRET_KEY = "your_secret_key_change_in_production"  # Should be in environment variable
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    # Password hashing
    pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

    @classmethod
    def hash_password(cls, password: str) -> str:
        """Hash a password"""
        return cls.pwd_context.hash(password)

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash"""
        return cls.pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def create_access_token(cls, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
        return encoded_jwt

    @classmethod
    def verify_token(cls, token: str) -> Optional[TokenData]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])
            user_name: str = payload.get("sub")
            user_id: int = payload.get("user_id")
            
            if user_name is None:
                return None
            
            return TokenData(user_name=user_name, user_id=user_id)
        except ExpiredSignatureError:
            return None
        except JWTError:
            return None
