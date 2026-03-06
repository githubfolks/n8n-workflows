import requests
import time
from src.config.settings import settings
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class VideoCreator:
    BASE_URL = "https://api.creatomate.com/v1/renders"

    def __init__(self):
        self.api_key = settings.creatomate_api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def create_video(self, modifications: Dict[str, Any]) -> str:
        """
        Creates a video based on the configured template and modifications.
        Returns the URL of the generated video.
        """
        payload = {
            "template_id": settings.creatomate_template_id,
            "modifications": modifications
        }

        try:
            logger.info("Triggering video render...")
            response = requests.post(self.BASE_URL, json=payload, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            render_id = data[0]['id']
            logger.info(f"Render started. ID: {render_id}")
            
            return self._poll_for_completion(render_id)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating video: {e}")
            if e.response:
                 logger.error(f"Response: {e.response.text}")
            raise

    def _poll_for_completion(self, render_id: str, timeout: int = 300) -> str:
        """
        Polls the API until the video rendering is complete.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.BASE_URL}/{render_id}", headers=self.headers)
                response.raise_for_status()
                data = response.json()
                status = data['status']
                
                if status == 'succeeded':
                    logger.info("Video render completed successfully.")
                    return data['url']
                elif status == 'failed':
                    error_msg = data.get('errorMessage', 'Unknown error')
                    raise Exception(f"Video render failed: {error_msg}")
                else:
                    logger.info(f"Rendering... Status: {status}")
                    time.sleep(5)
            except requests.exceptions.RequestException as e:
                logger.warning(f"Error polling render status: {e}")
                time.sleep(5)
                
        raise Exception("Video render timed out.")
