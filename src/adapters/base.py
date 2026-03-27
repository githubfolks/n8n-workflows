from abc import ABC, abstractmethod
from src.models.post import SocialContent
import logging

logger = logging.getLogger(__name__)

class SocialAdapter(ABC):
    """
    Abstract base class for all social media adapters.
    """
    
    @abstractmethod
    def post_text(self, content: SocialContent) -> str:
        """
        Posts text-only content.
        Returns the post ID or URL.
        """
        pass

    @abstractmethod
    def post_image(self, content: SocialContent) -> str:
        """
        Posts an image with caption.
        Returns the post ID or URL.
        """
        pass

    @abstractmethod
    def post_video(self, content: SocialContent) -> str:
        """
        Posts a video with caption.
        Returns the post ID or URL.
        """
        pass

    def post(self, content: SocialContent) -> str:
        """
        Determines the type of post and calls the appropriate method.
        """
        try:
            if content.video_url:
                return self.post_video(content)
            elif content.image_url:
                return self.post_image(content)
            else:
                return self.post_text(content)
        except Exception as e:
            logger.error(f"Error posting to {self.__class__.__name__}: {e}")
            raise
