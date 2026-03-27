from typing import Any, List
from fastapi import APIRouter, Depends, Body, Response, HTTPException, UploadFile, File, BackgroundTasks
from app.services.content import ContentService
from app.services.media import MediaService
from app.api import deps
from app.models.user import User
from app.core.config import settings
from minio import Minio
from datetime import timedelta
import httpx
import uuid
import io

from app.schemas.content import ContentGenerationRequest, GeneratedContent

router = APIRouter()

def _get_minio_client():
    return Minio(
        settings.MINIO_ENDPOINT.replace("http://", "").replace("https://", ""),
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_SECURE,
    )

@router.post("/content", response_model=GeneratedContent)
async def generate_content_api(
    request: ContentGenerationRequest,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Generate text content for a post.
    """
    service = ContentService()
    return await service.generate_text(request.topic, request.tone, request.platform)

@router.post("/image")
async def generate_image_api(
    prompt: str = Body(..., embed=True),
    current_user: User = Depends(deps.get_current_user),
) -> Response:
    """
    Generate an image and return raw binary.
    Also uploads to MinIO and returns a presigned URL in X-Image-Url header
    so other services (e.g. video-service) can fetch it without auth.
    """
    service = MediaService()
    url = await service.generate_image(prompt)

    # Download the image from the source URL (DALL-E / local)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            image_bytes = response.content
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch image: {e}")

    # Upload to MinIO and generate a presigned URL for other services
    try:
        minio_client = _get_minio_client()
        bucket = settings.MINIO_BUCKET_NAME
        if not minio_client.bucket_exists(bucket):
            minio_client.make_bucket(bucket)
        object_name = f"images/{uuid.uuid4()}.png"
        minio_client.put_object(
            bucket, object_name, io.BytesIO(image_bytes), len(image_bytes),
            content_type="image/png",
        )
        # Presigned URL valid for 1 hour — allows unauthenticated download
        minio_url = minio_client.presigned_get_object(bucket, object_name, expires=timedelta(hours=1))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload image to MinIO: {e}")

    return Response(
        content=image_bytes,
        media_type="image/png",
        headers={"X-Image-Url": minio_url},
    )

@router.post("/video")
async def generate_video_api(
    file: UploadFile = File(...),
    caption: str = Body(None),
    current_user: User = Depends(deps.get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks(),
) -> Response:
    """
    Generate a video from an uploaded image file and return raw binary MP4.
    Accepts multipart form data with a single image file.
    Can also accept a 'caption' string to generate a TTS voiceover.
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"generate_video_api called with file={file.filename}, content_type={file.content_type}, caption={caption}")

    minio_client = _get_minio_client()
    bucket = settings.MINIO_BUCKET_NAME
    try:
        if not minio_client.bucket_exists(bucket):
            minio_client.make_bucket(bucket)
    except Exception:
        pass
        
    service = MediaService()

    # Upload the image to MinIO and get a presigned URL
    image_urls = []
    try:
        img_bytes = await file.read()
        object_name = f"video-input/{uuid.uuid4()}.png"
        minio_client.put_object(
            bucket, object_name, io.BytesIO(img_bytes), len(img_bytes),
            content_type=file.content_type or "image/png",
        )
        presigned = minio_client.presigned_get_object(bucket, object_name, expires=timedelta(hours=1))
        image_urls.append(presigned)
        logger.info(f"Uploaded image to MinIO: {object_name}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload image to MinIO: {e}")
        
    audio_url = None
    if caption:
         try:
             audio_bytes = await service.generate_audio(caption)
             audio_object_name = f"audio-input/{uuid.uuid4()}.mp3"
             minio_client.put_object(
                 bucket, audio_object_name, io.BytesIO(audio_bytes), len(audio_bytes),
                 content_type="audio/mpeg",
             )
             audio_url = minio_client.presigned_get_object(bucket, audio_object_name, expires=timedelta(hours=1))
             logger.info(f"Generated and uploaded audio to MinIO: {audio_object_name}")
         except Exception as e:
             raise HTTPException(status_code=500, detail=f"Failed to generate TTS audio: {e}")

    # Call the video service
    service = MediaService()
    video_result_url = await service.generate_video(image_urls, audio_url, caption)

    # Download the generated video and return as binary
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(video_result_url, timeout=60.0)
            response.raise_for_status()
            return Response(
                content=response.content,
                media_type="video/mp4",
                headers={"Content-Disposition": "attachment; filename=video.mp4"},
            )
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch video: {e}")

@router.post("/post-video-to-facebook")
async def post_video_to_facebook(
    file: UploadFile = File(...),
    page_id: str = Body(...),
    access_token: str = Body(...),
    description: str = Body(""),
):
    """
    Upload a video directly to Facebook from the backend.
    This avoids n8n's multipart binary handling issues.
    """
    import logging
    logger = logging.getLogger(__name__)

    video_bytes = await file.read()
    logger.info(f"Posting video to Facebook: page_id={page_id}, size={len(video_bytes)}, description={description[:50]}...")

    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            resp = await client.post(
                f"https://graph-video.facebook.com/v19.0/{page_id}/videos",
                data={"access_token": access_token, "description": description},
                files={"source": ("video.mp4", video_bytes, "video/mp4")},
            )
            logger.info(f"Facebook response: {resp.status_code} {resp.text[:200]}")
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail=resp.text)
            return resp.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Facebook upload failed: {e}")

