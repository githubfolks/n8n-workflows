from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from app.services.video_engine import VideoEngine
from app.services.s3 import MinioService
import aiohttp
import asyncio
import logging
import uuid
import os

router = APIRouter()
logger = logging.getLogger(__name__)

class VideoGenerationRequest(BaseModel):
    image_urls: List[str]
    audio_url: Optional[str] = None
    captions: Optional[List[str]] = None

class VideoResponse(BaseModel):
    url: str

async def download_file(url: str, dest_path: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                with open(dest_path, 'wb') as f:
                    f.write(await response.read())
            else:
                raise Exception(f"Failed to download {url}")

@router.post("/generate", response_model=VideoResponse)
async def generate_video(request: VideoGenerationRequest):
    # Setup temporary workspace
    job_id = str(uuid.uuid4())
    work_dir = f"/tmp/{job_id}"
    os.makedirs(work_dir, exist_ok=True)
    
    try:
        # 1. Download Assets
        logger.info(f"Video generation request - image_urls: {request.image_urls}, audio_url: {request.audio_url}")
        image_paths = []
        for i, url in enumerate(request.image_urls):
            logger.info(f"Downloading image {i} from: {url}")
            path = f"{work_dir}/image_{i}.png" # Assumes png/jpg
            await download_file(url, path)
            image_paths.append(path)
            
        audio_path = None
        if request.audio_url:
            audio_path = f"{work_dir}/audio.mp3"
            await download_file(request.audio_url, audio_path)

        # 2. Render Video
        engine = VideoEngine(output_dir=work_dir)
        # Using run_in_executor for CPU bound ffmpeg task
        loop = asyncio.get_event_loop()
        output_path = await loop.run_in_executor(
            None, 
            engine.create_video, 
            image_paths, 
            audio_path,
            request.captions
        )
        
        # 3. Upload to MinIO
        minio = MinioService()
        minio_object_name = f"{job_id}.mp4"
        video_url = minio.upload_file(output_path, minio_object_name)
        
        return VideoResponse(url=video_url)

    except Exception as e:
        import traceback
        logger.error(f"Video generation failed: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup
        try:
             import shutil
             shutil.rmtree(work_dir)
        except:
            pass
