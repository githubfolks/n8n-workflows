from abc import ABC, abstractmethod
from typing import List, Optional

class SocialAdapter(ABC):
    @abstractmethod
    async def post_image(self, image_url: str, caption: str) -> str:
        """Uploads an image and returns the post ID/URL."""
        pass

    @abstractmethod
    async def post_video(self, video_url: str, caption: str) -> str:
        """Uploads a video and returns the post ID/URL."""
        pass
