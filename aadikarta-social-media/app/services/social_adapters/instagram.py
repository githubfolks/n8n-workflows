import logging
import aiohttp
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings
from app.services.social_adapters.base import SocialAdapter

logger = logging.getLogger(__name__)

class InstagramAdapter(SocialAdapter):
    def __init__(self):
        self.account_id = settings.INSTAGRAM_BUSINESS_ACCOUNT_ID
        self.access_token = settings.FACEBOOK_ACCESS_TOKEN # IG uses FB token
        self.base_url = f"https://graph.facebook.com/v19.0/{self.account_id}"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def post_image(self, image_url: str, caption: str) -> str:
        # 1. Create Media Container
        container_id = await self._create_container(image_url, caption, media_type="IMAGE")
        
        # 2. Publish Container
        return await self._publish_container(container_id)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def post_video(self, video_url: str, caption: str) -> str:
        # 1. Create Media Container (REELS)
        container_id = await self._create_container(video_url, caption, media_type="REELS")
        
        # 2. Wait for processing (Polling)
        await self._wait_for_processing(container_id)
        
        # 3. Publish
        return await self._publish_container(container_id)

    async def _create_container(self, url: str, caption: str, media_type: str) -> str:
        endpoint = f"{self.base_url}/media"
        params = {
            "caption": caption,
            "access_token": self.access_token,
        }
        if media_type == "IMAGE":
            params["image_url"] = url
        else:
            params["video_url"] = url
            params["media_type"] = "REELS"
            
        async with aiohttp.ClientSession() as session:
            async with session.post(endpoint, params=params) as response:
                if response.status != 200:
                    text = await response.text()
                    raise Exception(f"IG Create Container Failed: {text}")
                data = await response.json()
                return data["id"]

    async def _publish_container(self, creation_id: str) -> str:
        endpoint = f"{self.base_url}/media_publish"
        params = {
            "creation_id": creation_id,
            "access_token": self.access_token,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(endpoint, params=params) as response:
                if response.status != 200:
                    text = await response.text()
                    raise Exception(f"IG Publish Failed: {text}")
                data = await response.json()
                return data["id"]

    async def _wait_for_processing(self, container_id: str, max_retries=10):
        endpoint = f"https://graph.facebook.com/v19.0/{container_id}"
        params = {
            "fields": "status_code",
            "access_token": self.access_token
        }
        async with aiohttp.ClientSession() as session:
            for _ in range(max_retries):
                async with session.get(endpoint, params=params) as response:
                    data = await response.json()
                    status = data.get("status_code")
                    if status == "FINISHED":
                        return
                    elif status == "ERROR":
                        raise Exception("IG Media Processing Error")
                    await asyncio.sleep(5)
            raise Exception("IG Media Processing Timed Out")
