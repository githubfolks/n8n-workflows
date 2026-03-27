from minio import Minio
from app.core.config import settings
import io
import logging

logger = logging.getLogger(__name__)

class StorageService:
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

    async def upload_file(self, file_data: bytes, filename: str, content_type: str) -> str:
        """
        Uploads a file to MinIO and returns the URL.
        """
        try:
            file_stream = io.BytesIO(file_data)
            self.client.put_object(
                self.bucket_name,
                filename,
                file_stream,
                length=len(file_data),
                content_type=content_type
            )
            # Generate URL (presigned or public)
            # For simplicity, returning a presigned URL or constructed URL
            # If MinIO is public, we can construct the URL.
            # return self.client.presigned_get_object(self.bucket_name, filename)
            
            # Assuming public access or internal network usage:
            return f"http://{settings.MINIO_ENDPOINT}/{self.bucket_name}/{filename}"
            
        except Exception as e:
            logger.error(f"Error uploading file to MinIO: {e}")
            raise
