from datetime import timedelta
from typing import Any, Union, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core import security
from app.core.config import settings
from app.models.user import User

class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def authenticate(self, email: str, password: str) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        if not user:
            return None
        if not security.verify_password(password, user.hashed_password):
            return None
        return user

    def create_token(self, user: User) -> Any:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return {
            "access_token": security.create_access_token(
                user.id, expires_delta=access_token_expires
            ),
            "token_type": "bearer",
        }
