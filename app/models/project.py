from datetime import datetime
from typing import Optional, List, Any
from sqlmodel import Field, SQLModel
from sqlalchemy import JSON, Column

class ProjectBase(SQLModel):
    topic_prompt: str
    generated_story: str
    scenes_json: List[Any] = Field(default=[], sa_column=Column(JSON))
    status: str = "draft"  # draft, publishing, completed, failed
    video_path: Optional[str] = None

class Project(ProjectBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ProjectCreate(ProjectBase):
    pass

class ProjectRead(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime

class ProjectUpdate(SQLModel):
    topic_prompt: Optional[str] = None
    generated_story: Optional[str] = None
    scenes_json: Optional[List[Any]] = None
    status: Optional[str] = None
    video_path: Optional[str] = None
