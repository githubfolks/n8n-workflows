from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel
from sqlalchemy import JSON, Column

class PostBase(SQLModel):
    topic: str
    content: str
    platforms: List[str] = Field(default=[], sa_column=Column(JSON))
    scheduled_at: Optional[datetime] = None
    status: str = "draft" # draft, scheduled, published, failed
    image_url: Optional[str] = None
    video_url: Optional[str] = None

class Post(PostBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    owner_id: int = Field(foreign_key="user.id")

class PostCreate(PostBase):
    pass

class PostRead(PostBase):
    id: int
    created_at: datetime
    owner_id: int

class PostUpdate(SQLModel):
    topic: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None
