from minio import Minio
from app.core.config import settings
from datetime import timedelta
import logging

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

    def upload_file(self, file_path: str, object_name: str) -> str:
        """
        Uploads a file to MinIO and returns a presigned URL.
        """
        try:
            self.client.fput_object(
                self.bucket_name,
                object_name,
                file_path,
                content_type="video/mp4"
            )
            # Return presigned URL so callers can download without MinIO credentials
            return self.client.presigned_get_object(
                self.bucket_name, object_name, expires=timedelta(hours=1)
            )
        except Exception as e:
            logger.error(f"Error uploading video to MinIO: {e}")
            raise

