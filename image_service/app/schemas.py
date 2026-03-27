from pydantic import BaseModel
from typing import List, Optional

class ImageGenerationRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = "ugly, blurry, low quality"
    width: int = 512
    height: int = 512
    steps: int = 20
    cfg_scale: float = 7.0
    count: int = 1

class ImageResponse(BaseModel):
    urls: List[str]

class BatchGenerationRequest(BaseModel):
    prompts: List[str]
    negative_prompt: Optional[str] = ""
