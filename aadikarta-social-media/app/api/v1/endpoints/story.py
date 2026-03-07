from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel
from typing import List
from app.services.story import StoryService

router = APIRouter()

class StoryRequest(BaseModel):
    topic: str

class ScenesRequest(BaseModel):
    story: str

class SceneResponse(BaseModel):
    id: int
    description: str

@router.post("/generate-story", response_model=dict)
async def generate_story_api(request: StoryRequest):
    """
    Generate a 3-part 30-second video script from a given topic.
    """
    try:
        service = StoryService()
        story_text = await service.generate_story(request.topic)
        return {"story": story_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-scenes", response_model=List[SceneResponse])
async def generate_scenes_api(request: ScenesRequest):
    """
    Parse a story script and generate discrete visual scenes.
    """
    try:
        service = StoryService()
        scenes = await service.generate_scenes(request.story)
        return scenes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
