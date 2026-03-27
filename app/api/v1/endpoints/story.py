from fastapi import APIRouter, Body, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Any
import os
import aiofiles
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.story import StoryService
from app.core.db import get_session
from app.models.project import Project

router = APIRouter()

class StoryRequest(BaseModel):
    topic: str

class ScenesRequest(BaseModel):
    story: str

class SceneResponse(BaseModel):
    id: int
    description: str

class SaveDraftRequest(BaseModel):
    topic: str
    story: str
    scenes: List[Any]

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

@router.post("/save-draft")
async def save_draft_api(request: SaveDraftRequest, db: AsyncSession = Depends(get_session)):
    """
    Save the generated topic, story, and scenes to the database.
    """
    try:
        new_project = Project(
            topic_prompt=request.topic,
            generated_story=request.story,
            scenes_json=request.scenes,
            status="draft"
        )
        db.add(new_project)
        await db.commit()
        await db.refresh(new_project)
        return {"project_id": new_project.id, "status": "draft"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/publish-project/{project_id}")
async def publish_project_api(project_id: int, db: AsyncSession = Depends(get_session)):
    """
    Mark project as publishing and forward to n8n Webhook.
    """
    try:
        # 1. Fetch the project
        project = await db.get(Project, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # 2. Update status
        project.status = "publishing"
        db.add(project)
        await db.commit()

        # 3. Trigger n8n webhook
        import httpx
        async with httpx.AsyncClient() as client:
            webhook_url = "http://n8n:5678/webhook-test/generate-video"
            n8n_payload = {
                "project_id": project.id,
                "story": project.generated_story,
                "scenes": project.scenes_json
            }
            # We don't await the response in production to avoid hanging if n8n takes 5 minutes to render
            # But for simple testing we can fire and forget or await the immediate 200 OK from webhook
            response = await client.post(webhook_url, json=n8n_payload, timeout=10.0)
            response.raise_for_status()

        return {"status": "publishing", "message": "Successfully sent to n8n"}
    except httpx.HTTPError as he:
        # If n8n fails to reply
        raise HTTPException(status_code=502, detail=f"Failed to trigger n8n: {str(he)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook/n8n/video-completed")
async def n8n_video_completed_webhook(
    project_id: int = Form(...),
    video_file: UploadFile = File(...),
    db: AsyncSession = Depends(get_session)
):
    """
    Webhook for n8n to call when video rendering and uploading is fully complete.
    Accepts the project_id and the raw .mp4 file to save for future reuse.
    """
    try:
        # 1. Fetch the project
        project = await db.get(Project, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # 2. Save the video physically to the backend disk
        # In production this could be uploaded to S3
        upload_dir = "app/media/videos"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = f"{upload_dir}/{project_id}_{video_file.filename}"
        
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await video_file.read()
            await out_file.write(content)
        
        # 3. Update the database URL
        project.video_path = file_path
        project.status = "completed"
        db.add(project)
        await db.commit()

        return {"status": "success", "saved_path": file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects", response_model=List[Project])
async def list_projects_api(db: AsyncSession = Depends(get_session)):
    """
    Fetch all past story projects for the dashboard, newest first.
    """
    from sqlalchemy.future import select
    try:
        result = await db.execute(select(Project).order_by(Project.created_at.desc()))
        projects = result.scalars().all()
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}", response_model=Project)
async def get_project_api(project_id: int, db: AsyncSession = Depends(get_session)):
    """
    Fetch a single project's details.
    """
    try:
        project = await db.get(Project, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


