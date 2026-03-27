from typing import List
from openai import OpenAI
import requests
import logging
import asyncio
from app.core.config import settings

logger = logging.getLogger(__name__)

class MediaService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

    async def generate_image(self, prompt: str, use_local: bool = False) -> str:
        """
        Generates an image URL using DALL-E 3 or Local Image Service.
        """
        if use_local:
             return await self._generate_image_local(prompt)

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._generate_image_sync, prompt)

    async def _generate_image_local(self, prompt: str) -> str:
        try:
            payload = {"prompt": prompt, "count": 1}
            # Using aiohttp or requests (if sync wrapper needed, but we are in async method)
            # For simplicity using requests in executor or just standard http
            # Let's use simple requests for now or assume aiohttp is available if we installed it.
            # We didn't install aiohttp in the main app requirements, only requests.
            response = requests.post(f"{settings.IMAGE_SERVICE_URL}/generate", json=payload)
            response.raise_for_status()
            data = response.json()
            return data['urls'][0]
        except Exception as e:
            logger.error(f"Error generating image locally: {e}")
            raise

    def _generate_image_sync(self, prompt: str) -> str:
        try:
            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            return response.data[0].url
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            raise

    async def generate_audio(self, text: str) -> bytes:
        """
        Generates TTS audio using OpenAI and returns the binary mp3 data.
        """
        logger.info("Generating TTS audio via OpenAI")
        loop = asyncio.get_event_loop()
        
        def run_tts():
            response = self.openai_client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=text
            )
            return response.content
            
        return await loop.run_in_executor(None, run_tts)

    async def generate_video(self, image_urls: List[str], audio_url: str = None, captions: str = None) -> str:
        """
        Generates a video URL using Local Video Service.
        Now uses Replicate SVD for animation prior to passing to local video engine
        """
        # Step 1: Animate the first image using Replicate
        animated_video_url = await self._generate_video_replicate(image_urls[0])
        
        # Step 2: Pass animated video to local video service for audio/captions
        # (For now passing the animated URL instead of the image list)
        return await self._generate_video_local([animated_video_url], audio_url, captions)

    async def _generate_video_replicate(self, image_url: str) -> str:
        """
        Calls Replicate's Stable Video Diffusion API to animate an image
        """
        import replicate
        logger.info("Calling Replicate SVD API for Image-to-Video animation")
        
        loop = asyncio.get_event_loop()
        
        def run_replicate():
            if not settings.REPLICATE_API_TOKEN:
                 raise ValueError("REPLICATE_API_TOKEN is not set in environment")
            
            # Using stability-ai/stable-video-diffusion:3f0457e4619daac51203dedb472816fd4af51f3149fa7a9e0b5ffcf1b8172438
            output = replicate.run(
                "stability-ai/stable-video-diffusion:3f0457e4619daac51203dedb472816fd4af51f3149fa7a9e0b5ffcf1b8172438",
                input={
                    "cond_aug": 0.02,
                    "decoding_t": 14,
                    "input_image": image_url,
                    "video_length": "14_frames_with_svd",
                    "sizing_strategy": "maintain_aspect_ratio",
                    "motion_bucket_id": 127,
                    "frames_per_second": 6
                }
            )
            # Output is a URI pointing to the mp4 file
            return output

        return await loop.run_in_executor(None, run_replicate)

    async def _generate_video_local(self, video_urls: List[str], audio_url: str = None, captions: str = None) -> str:
        try:
            payload = {
                "image_urls": video_urls, # We pass the single animated video URL here now as if it were an image
                "audio_url": audio_url,
                "captions": [captions] if captions else None
            }
            # As before, simple requests wrapper for now
            response = requests.post(f"{settings.VIDEO_SERVICE_URL}/generate", json=payload)
            response.raise_for_status()
            data = response.json()
            return data['url']
        except Exception as e:
             logger.error(f"Error generating video locally: {e}")
             raise
