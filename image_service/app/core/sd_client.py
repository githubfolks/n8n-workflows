import aiohttp
import logging
import base64
from app.core.config import settings
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class SDClient:
    def __init__(self):
        self.api_url = settings.SD_API_URL

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def txt2img(self, prompt: str, negative_prompt: str = "", steps: int = 20, cfg_scale: float = 7.0, width: int = 512, height: int = 512):
        """
        Calls the Stable Diffusion txt2img API.
        """
        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "width": width,
            "height": height,
            "sampler_name": "Euler a",
            "batch_size": 1,
            "n_iter": 1,
        }
        
        url = f"{self.api_url}/sdapi/v1/txt2img"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"SD API Error: {response.status} - {error_text}")
                        raise Exception(f"SD API Error: {response.status}")
                    
                    data = await response.json()
                    # A1111 returns 'images': [base64_string, ...]
                    return data['images'][0]
            except aiohttp.ClientError as e:
                logger.error(f"Network error connecting to SD API: {e}")
                raise
