from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.core import security
from app.core.config import settings
from app.models.user import User, UserCreate, UserRead, UserUpdate
from app.services.auth import AuthService

router = APIRouter()

@router.post("/login/access-token")
async def login_access_token(
    session: AsyncSession = Depends(deps.get_session),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    auth_service = AuthService(session)
    user = await auth_service.authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return auth_service.create_token(user)

@router.post("/signup", response_model=UserRead)
async def create_user(
    *,
    session: AsyncSession = Depends(deps.get_session),
    user_in: UserCreate,
) -> Any:
    # Check if user exists
    from sqlalchemy.future import select
    result = await session.execute(select(User).where(User.email == user_in.email))
    if result.scalars().first():
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
        
    user = User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        full_name=user_in.full_name,
        is_superuser=user_in.is_superuser,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
