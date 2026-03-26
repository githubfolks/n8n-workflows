from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from sqlmodel import SQLModel

# Import all models to ensure SQLModel registers them
from app.models.user import User
from app.models.post import Post
from app.models.project import Project

from sqlalchemy.engine.url import make_url

url = make_url(settings.DATABASE_URL)
connect_args = {}

# Handle search_path from query options (e.g., ?options=-csearch_path=schema_name)
if "options" in url.query:
    options = url.query["options"]
    if "search_path=" in options:
        schema = options.split("search_path=")[1].split()[0].replace(",", "")
        connect_args["server_settings"] = {"search_path": schema}
    
    # Remove options from URL to prevent asyncpg from getting confused
    query = dict(url.query)
    del query["options"]
    url = url.set(query=query)

engine = create_async_engine(
    url,
    echo=True,
    future=True,
    connect_args=connect_args
)

async def init_db():
    async with engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncSession:
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
