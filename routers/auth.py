import logging
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from settings.db import get_db
from models.user import User
from schemas.user import UserCreate, UserRead, Token
from utils.security import security, verify_password, get_password_hash

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Authentication"])

SessionDepend = Annotated[AsyncSession, Depends(get_db)]

# Реєстрація нового користувача
@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, session: SessionDepend):
    try:
        result = await session.execute(select(User).where(User.email == user_data.email))
        if result.scalars().first():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
        new_user = User(email=user_data.email, hashed_password=get_password_hash(user_data.password))
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to register user")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to register user") from exc

# Логін та видача JWT-токена
@router.post("/login", response_model=Token)
async def login(credentials: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDepend):
    try:
        result = await session.execute(select(User).where(User.email == credentials.username))
        user = result.scalars().first()
        if not user or not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
        access_token = security.create_access_token(uid=str(user.id))
        return Token(access_token=access_token, token_type="bearer")
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to login user")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to login") from exc
