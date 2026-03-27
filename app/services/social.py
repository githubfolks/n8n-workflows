import logging
from app.services.social_adapters.facebook import FacebookAdapter
from app.services.social_adapters.instagram import InstagramAdapter
from app.services.social_adapters.youtube import YouTubeAdapter
from app.services.social_adapters.twitter import TwitterAdapter

logger = logging.getLogger(__name__)

class SocialService:
    def __init__(self):
        self.fb = FacebookAdapter()
        self.ig = InstagramAdapter()
        self.yt = YouTubeAdapter()
        self.tw = TwitterAdapter()

    async def post_to_platform(self, platform: str, content: str, media_url: str, media_type: str = "image"):
        """
        Publishes content to the specified platform using the appropriate adapter.
        """
        try:
            adapter = None
            if platform == "facebook":
                adapter = self.fb
            elif platform == "instagram":
                adapter = self.ig
            elif platform == "youtube":
                adapter = self.yt
            elif platform == "twitter":
                adapter = self.tw
            else:
                raise ValueError(f"Unknown platform: {platform}")

            if media_type == "image":
                return await adapter.post_image(media_url, content)
            elif media_type == "video":
                return await adapter.post_video(media_url, content)
            else:
                raise ValueError("Unsupported media type")
                
        except Exception as e:
            logger.error(f"Failed to post to {platform}: {e}")
            raise
