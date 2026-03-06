import logging
import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings
from app.services.social_adapters.base import SocialAdapter

logger = logging.getLogger(__name__)

class FacebookAdapter(SocialAdapter):
    def __init__(self):
        self.page_id = settings.FACEBOOK_PAGE_ID
        self.access_token = settings.FACEBOOK_ACCESS_TOKEN
        self.base_url = f"https://graph.facebook.com/v19.0/{self.page_id}"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def post_image(self, image_url: str, caption: str) -> str:
        url = f"{self.base_url}/photos"
        params = {
            "url": image_url,
            "message": caption,
            "access_token": self.access_token,
            "published": "true"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, params=params) as response:
                if response.status != 200:
                    error = await response.text()
                    logger.error(f"Facebook Image Upload Failed: {error}")
                    raise Exception(f"Facebook Image Upload Failed: {error}")
                data = await response.json()
                return data.get("id")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def post_video(self, video_url: str, caption: str) -> str:
        # Facebook Video Upload (non-resumable for simplicity, suitable for shorts)
        url = f"{self.base_url}/videos"
        params = {
            "file_url": video_url,
            "description": caption,
            "access_token": self.access_token
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, params=params) as response:
                if response.status != 200:
                    error = await response.text()
                    logger.error(f"Facebook Video Upload Failed: {error}")
                    raise Exception(f"Facebook Video Upload Failed: {error}")
                data = await response.json()
                return data.get("id")
