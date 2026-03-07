from fastapi import APIRouter
from app.api.v1.endpoints import auth, posts, generate, story

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(posts.router, prefix="/posts", tags=["posts"])
api_router.include_router(generate.router, prefix="/generate", tags=["generate"])
api_router.include_router(story.router, prefix="/story", tags=["story"])
