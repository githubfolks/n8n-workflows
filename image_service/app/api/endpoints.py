from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.schemas import ImageGenerationRequest, ImageResponse, BatchGenerationRequest
from app.core.sd_client import SDClient
from app.services.s3 import MinioService
import asyncio
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/generate", response_model=ImageResponse)
async def generate_image(request: ImageGenerationRequest):
    sd_client = SDClient()
    minio_service = MinioService()
    
    urls = []
    
    # Generate 'count' images
    # A1111 batch_size is one way, or we can loop. 
    # Looping gives more control if we want distinct seeds or monitoring.
    
    for _ in range(request.count):
        try:
            # 1. Generate Base64
            base64_image = await sd_client.txt2img(
                prompt=request.prompt,
                negative_prompt=request.negative_prompt,
                width=request.width,
                height=request.height,
                steps=request.steps,
                cfg_scale=request.cfg_scale
            )
            
            # 2. Upload to MinIO
            url = minio_service.upload_base64_image(base64_image)
            urls.append(url)
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
            
    return ImageResponse(urls=urls)

@router.post("/batch", response_model=ImageResponse)
async def generate_batch(request: BatchGenerationRequest):
    # Simple sequential batch for now. 
    # Use background tasks or a queue for real heavy loads.
    sd_client = SDClient()
    minio_service = MinioService()
    urls = []
    
    for prompt in request.prompts:
        try:
            base64_image = await sd_client.txt2img(
                prompt=prompt,
                negative_prompt=request.negative_prompt
            )
            url = minio_service.upload_base64_image(base64_image)
            urls.append(url)
        except Exception as e:
            logger.error(f"Batch item failed for prompt '{prompt}': {e}")
            # Continue or fail? Let's fail hard for now to signal issues.
            raise HTTPException(status_code=500, detail=f"Failed on prompt: {prompt}")

    return ImageResponse(urls=urls)
