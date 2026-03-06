import requests
from src.adapters.base import SocialAdapter
from src.models.post import SocialContent
from src.config.settings import settings
import logging

logger = logging.getLogger(__name__)

class FacebookAdapter(SocialAdapter):
    def __init__(self):
        self.page_id = settings.facebook_page_id
        self.access_token = settings.facebook_access_token
        self.base_url = f"https://graph.facebook.com/v19.0/{self.page_id}"

    def post_text(self, content: SocialContent) -> str:
        url = f"{self.base_url}/feed"
        data = {
            "message": content.full_caption,
            "access_token": self.access_token
        }
        return self._make_request(url, data)

    def post_image(self, content: SocialContent) -> str:
        url = f"{self.base_url}/photos"
        data = {
            "message": content.full_caption,
            "url": content.image_url,
            "access_token": self.access_token
        }
        return self._make_request(url, data)

    def post_video(self, content: SocialContent) -> str:
        # Posting video to Page Feed
        # Step 1: Initialize upload (optional generally for small videos, but good practice)
        # For simplicity, we'll try direct URL upload first for hosted videos
        url = f"{self.base_url}/videos"
        data = {
            "description": content.full_caption,
            "file_url": content.video_url,
            "access_token": self.access_token
        }
        return self._make_request(url, data)

    def _make_request(self, url: str, data: dict) -> str:
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            result = response.json()
            post_id = result.get('id') or result.get('post_id')
            logger.info(f"Successfully posted to Facebook. ID: {post_id}")
            return post_id
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to post to Facebook: {e}")
            if e.response:
                logger.error(f"Response: {e.response.text}")
            raise
