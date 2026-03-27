from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.api import deps
from app.models.post import Post, PostCreate, PostRead, PostUpdate
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[PostRead])
async def read_posts(
    session: AsyncSession = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    query = select(Post).where(Post.owner_id == current_user.id).offset(skip).limit(limit)
    result = await session.execute(query)
    return result.scalars().all()

@router.post("/", response_model=PostRead)
async def create_post(
    *,
    session: AsyncSession = Depends(deps.get_session),
    post_in: PostCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    post = Post.from_orm(post_in)
    post.owner_id = current_user.id
    session.add(post)
    await session.commit()
    await session.refresh(post)
    return post
