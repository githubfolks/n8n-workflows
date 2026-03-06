import requests
from src.adapters.base import SocialAdapter
from src.models.post import SocialContent
from src.config.settings import settings
import logging
import time

logger = logging.getLogger(__name__)

class InstagramAdapter(SocialAdapter):
    def __init__(self):
        self.account_id = settings.instagram_business_account_id
        self.access_token = settings.facebook_access_token # IG uses FB token
        self.base_url = f"https://graph.facebook.com/v19.0/{self.account_id}"

    def post_text(self, content: SocialContent) -> str:
        logger.warning("Instagram does not support text-only posts. Skipping.")
        return None

    def post_image(self, content: SocialContent) -> str:
        # Step 1: Create Media Container
        container_id = self._create_media_container(
            image_url=content.image_url,
            caption=content.full_caption
        )
        # Step 2: Publish Container
        return self._publish_container(container_id)

    def post_video(self, content: SocialContent) -> str:
        # Step 1: Create Media Container for Video (Reels)
        container_id = self._create_media_container(
            video_url=content.video_url,
            caption=content.full_caption,
            media_type="VIDEO"
        )
        
        # Check status before publishing (video processing takes time)
        self._wait_for_media_processing(container_id)

        # Step 2: Publish Container
        return self._publish_container(container_id)

    def _create_media_container(self, caption: str, image_url: str = None, video_url: str = None, media_type: str = "IMAGE") -> str:
        url = f"{self.base_url}/media"
        data = {
            "access_token": self.access_token,
            "caption": caption
        }
        
        if media_type == "IMAGE":
            data["image_url"] = image_url
        elif media_type == "VIDEO":
            data["media_type"] = "REELS" # Usually aiming for Reels
            data["video_url"] = video_url
            
        response = requests.post(url, data=data)
        response.raise_for_status()
        return response.json()['id']

    def _wait_for_media_processing(self, container_id: str):
        url = f"https://graph.facebook.com/v19.0/{container_id}"
        params = {
            "access_token": self.access_token,
            "fields": "status_code"
        }
        
        for _ in range(10): # polling for 50 seconds max
            response = requests.get(url, params=params)
            data = response.json()
            status = data.get('status_code')
            
            if status == 'FINISHED':
                return
            elif status == 'ERROR':
                raise Exception("Instagram media processing failed.")
            
            time.sleep(5)
            
        logger.warning("Timeout waiting for Instagram media processing. Attempting publish anyway.")

    def _publish_container(self, creation_id: str) -> str:
        url = f"{self.base_url}/media_publish"
        data = {
            "creation_id": creation_id,
            "access_token": self.access_token
        }
        response = requests.post(url, data=data)
        response.raise_for_status()
        post_id = response.json()['id']
        logger.info(f"Successfully posted to Instagram. ID: {post_id}")
        return post_id
