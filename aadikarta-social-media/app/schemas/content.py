from pydantic import BaseModel
from typing import List, Optional

class ContentGenerationRequest(BaseModel):
    topic: str
    tone: Optional[str] = "professional" # motivational, funny, etc.
    platform: Optional[str] = "generic" # instagram, twitter, linkedin

class GeneratedContent(BaseModel):
    caption: str
    hashtags: List[str]
    image_prompt: str
    video_script: Optional[str] = None
