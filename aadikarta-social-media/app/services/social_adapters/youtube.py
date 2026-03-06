import logging
import asyncio
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2.credentials import Credentials
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings
from app.services.social_adapters.base import SocialAdapter
import aiohttp
import io

logger = logging.getLogger(__name__)

class YouTubeAdapter(SocialAdapter):
    def __init__(self):
        # Assuming we have a refresh token or full credentials stored/constructed
        # For simplicity, we assume we can construct Credentials from env vars
        # In production, you might need a proper OAuth flow or service account (if allowed)
        # But for YouTube User uploads, OAuth Web Server flow is needed.
        # Here we assume token/refresh_token are available effectively.
        self.credentials = Credentials(
            token=None,
            refresh_token=settings.YOUTUBE_REFRESH_TOKEN,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.YOUTUBE_CLIENT_ID,
            client_secret=settings.YOUTUBE_CLIENT_SECRET
        )
        self.youtube = build("youtube", "v3", credentials=self.credentials)

    async def post_image(self, image_url: str, caption: str) -> str:
        # YouTube Community tab images require different access, skipping for now
        # or treat as not supported.
        logger.warning("YouTube image posting not fully supported in this adapter version.")
        return "skipped"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def post_video(self, video_url: str, caption: str) -> str:
        # 1. Download video to stream
        async with aiohttp.ClientSession() as session:
            async with session.get(video_url) as resp:
                if resp.status != 200:
                    raise Exception(f"Failed to download video from {video_url}")
                video_data = io.BytesIO(await resp.read())

        # 2. Upload
        # Running sync google api call in executor
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._upload_sync, video_data, caption)

    def _upload_sync(self, video_data, caption):
        body = {
            "snippet": {
                "title": caption[:100], # Title limit
                "description": caption,
                "tags": ["shorts", "ai"],
                "categoryId": "22" # People & Blogs
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        }
        
        media = MediaIoBaseUpload(video_data, mimetype="video/mp4", resumable=True)
        request = self.youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                logger.info(f"Uploaded {int(status.progress() * 100)}%")
        
        return response.get("id")
