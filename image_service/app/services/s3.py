from minio import Minio
from app.core.config import settings
import io
import logging
import base64
import uuid

logger = logging.getLogger(__name__)

class MinioService:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT.replace("http://", "").replace("https://", ""),
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
        except Exception as e:
            logger.error(f"Error checking/creating bucket: {e}")

    def upload_base64_image(self, base64_string: str) -> str:
        """
        Uploads a base64 encoded image to MinIO and returns the URL.
        """
        try:
            image_data = base64.b64decode(base64_string)
            file_stream = io.BytesIO(image_data)
            filename = f"{uuid.uuid4()}.png"
            
            self.client.put_object(
                self.bucket_name,
                filename,
                file_stream,
                length=len(image_data),
                content_type="image/png"
            )
            
            # Construct URL (assuming public or internal access)
            return f"http://{settings.MINIO_ENDPOINT}/{self.bucket_name}/{filename}"
            
        except Exception as e:
            logger.error(f"Error uploading image to MinIO: {e}")
            raise
