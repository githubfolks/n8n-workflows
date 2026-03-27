from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class SocialContent(BaseModel):
    """
    Represents the content to be posted to social media.
    """
    text: str
    image_url: Optional[str] = None
    image_prompt: Optional[str] = None
    video_url: Optional[str] = None
    hashtags: List[str] = []

    @property
    def full_caption(self) -> str:
        tag_string = " ".join(self.hashtags)
        return f"{self.text}\n\n{tag_string}"

class ContentRequest(BaseModel):
    """
    Request payload for generating content.
    """
    topic: str
    platform: List[str] = ["facebook", "instagram"]
    include_image: bool = True
    include_video: bool = False
