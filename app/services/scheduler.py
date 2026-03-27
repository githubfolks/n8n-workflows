from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.social import SocialService
from app.core.db import engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.post import Post
from sqlalchemy.future import select
from datetime import datetime
import logging
import asyncio

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()



async def check_scheduled_posts():
    """
    Checks for posts that need to be published.
    """
    logger.info("Checking for scheduled posts...")
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        # Find posts that are scheduled and due, and not yet published
        query = select(Post).where(
            Post.status == "scheduled",
            Post.scheduled_at <= datetime.utcnow()
        )
        result = await session.execute(query)
        posts = result.scalars().all()
        
        if not posts:
            return

        logger.info(f"Found {len(posts)} due posts.")
        social_service = SocialService()
        
        for post in posts:
            try:
                logger.info(f"Publishing Post ID {post.id}...")
                await social_service.publish(post)
                post.status = "published"
                session.add(post)
            except Exception as e:
                logger.error(f"Failed to publish Post ID {post.id}: {e}")
                post.status = "failed"
                session.add(post)
        
        await session.commit()

def start_scheduler():
    scheduler.add_job(check_scheduled_posts, "interval", minutes=1)
    scheduler.start()
