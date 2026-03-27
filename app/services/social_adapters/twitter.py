import logging
import aiohttp
import asyncio
from requests_oauthlib import OAuth1
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings
from app.services.social_adapters.base import SocialAdapter

logger = logging.getLogger(__name__)

class TwitterAdapter(SocialAdapter):
    def __init__(self):
        self.auth = OAuth1(
            settings.TWITTER_CONSUMER_KEY,
            settings.TWITTER_CONSUMER_SECRET,
            settings.TWITTER_ACCESS_TOKEN,
            settings.TWITTER_ACCESS_TOKEN_SECRET
        )
        self.media_url = "https://upload.twitter.com/1.1/media/upload.json"
        self.tweet_url = "https://api.twitter.com/2/tweets"

    async def post_image(self, image_url: str, caption: str) -> str:
        # 1. Download
        data = await self._download_media(image_url)
        
        # 2. Upload Media (Sync wrapper usually easier for oauth1 libraries or use requests)
        loop = asyncio.get_event_loop()
        media_id = await loop.run_in_executor(None, self._upload_media_sync, data, "image/jpeg")
        
        # 3. Post Tweet
        return await self._post_tweet(caption, [media_id])

    async def post_video(self, video_url: str, caption: str) -> str:
        # 1. Download
        data = await self._download_media(video_url)
        
        # 2. Upload Video (Chunked)
        loop = asyncio.get_event_loop()
        media_id = await loop.run_in_executor(None, self._upload_video_chunked_sync, data)
        
        # 3. Post Tweet
        return await self._post_tweet(caption, [media_id])

    async def _download_media(self, url: str) -> bytes:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    raise Exception("Failed to download media")
                return await resp.read()

    def _upload_media_sync(self, data: bytes, mime: str) -> str:
        files = {"media": data}
        r = requests.post(self.media_url, files=files, auth=self.auth)
        r.raise_for_status()
        return r.json()["media_id_string"]

    def _upload_video_chunked_sync(self, data: bytes) -> str:
        # INIT
        total_bytes = len(data)
        init_data = {
            "command": "INIT",
            "media_type": "video/mp4",
            "total_bytes": total_bytes,
            "media_category": "tweet_video"
        }
        r = requests.post(self.media_url, data=init_data, auth=self.auth)
        r.raise_for_status()
        media_id = r.json()["media_id_string"]

        # APPEND
        segment_id = 0
        chunk_size = 4 * 1024 * 1024
        import io
        f = io.BytesIO(data)
        
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            
            requests.post(
                self.media_url,
                data={
                    "command": "APPEND",
                    "media_id": media_id,
                    "segment_index": segment_id
                },
                files={"media": chunk},
                auth=self.auth
            ).raise_for_status()
            segment_id += 1

        # FINALIZE
        r = requests.post(
            self.media_url,
            data={"command": "FINALIZE", "media_id": media_id},
            auth=self.auth
        )
        r.raise_for_status()
        
        # Check processing info
        processing_info = r.json().get("processing_info")
        if processing_info:
            state = processing_info["state"]
            # Ideally loop check status here
            pass
            
        return media_id

    async def _post_tweet(self, text: str, media_ids: list) -> str:
        payload = {"text": text}
        if media_ids:
            payload["media"] = {"media_ids": media_ids}
            
        # Using requests for OAuth1 properly with requests-oauthlib
        loop = asyncio.get_event_loop()
        def _send():
            r = requests.post(self.tweet_url, json=payload, auth=self.auth)
            r.raise_for_status()
            return r.json()["data"]["id"]
            
        return await loop.run_in_executor(None, _send)
