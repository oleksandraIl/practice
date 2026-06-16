from typing import Annotated
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from authx import AuthX, AuthXConfig, RequestToken
from passlib.context import CryptContext

config = AuthXConfig()
config.JWT_SECRET_KEY = "your-super-secret-key"
config.JWT_ACCESS_COOKIE_NAME = "my_access_token"
config.JWT_TOKEN_LOCATION = ["headers"]

security = AuthX(config=config)

# Схема для Swagger: показує кнопку Authorize і надсилає токен у заголовку
bearer_scheme = HTTPBearer(auto_error=False)

# Залежність: вимагає валідний токен (через bearer_scheme Swagger надсилає заголовок)
async def require_token(
    _: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    token: Annotated[RequestToken, Depends(security.access_token_required)],
) -> RequestToken:
    return token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
