from typing import List, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Social Media Automation Backend"
    
    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Database
    DATABASE_URL: str
    
    # MinIO
    MINIO_ENDPOINT: str = ""
    MINIO_ACCESS_KEY: str = ""
    MINIO_SECRET_KEY: str = ""
    MINIO_BUCKET_NAME: str = "social-media-assets"
    MINIO_SECURE: bool = False
    
    # AI Services
    OPENAI_API_KEY: str
    REPLICATE_API_TOKEN: str = ""
    LLM_PROVIDER: str = "openai" # openai, lm_studio
    
    # LM Studio Settings
    LM_STUDIO_BASE_URL: str = "http://host.docker.internal:1234/v1"
    
    # Image Service
    IMAGE_SERVICE_URL: str = "http://image-service:8001"
    
    # Video Service
    VIDEO_SERVICE_URL: str = "http://video-service:8002"
    
    # n8n
    N8N_WEBHOOK_URL: str = "https://n8n.aadikarta.org"
    
    # CORS
    BACKEND_CORS_ORIGINS: Union[List[str], str] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    return [i.strip() for i in v.split(",")]
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError(v)
    
    @validator("N8N_WEBHOOK_URL", pre=True)
    def assemble_n8n_url(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip()
            if v and not v.startswith(("http://", "https://")):
                return f"http://{v}"
        return v

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")

settings = Settings()
