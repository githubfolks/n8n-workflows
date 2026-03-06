from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent.parent / ".env"),
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )

    # Database
    database_url: str = Field(..., alias="DATABASE_URL")

    # OpenAI
    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")

    # Creatomate
    creatomate_api_key: str = Field(..., alias="CREATOMATE_API_KEY")
    creatomate_template_id: str = Field(..., alias="CREATOMATE_TEMPLATE_ID")

    # Social Media - Facebook
    facebook_page_id: str = Field(..., alias="FACEBOOK_PAGE_ID")
    facebook_access_token: str = Field(..., alias="FACEBOOK_ACCESS_TOKEN")

    # Social Media - Instagram
    instagram_business_account_id: str = Field(..., alias="INSTAGRAM_BUSINESS_ACCOUNT_ID")

    # Social Media - YouTube
    youtube_client_id: str = Field(..., alias="YOUTUBE_CLIENT_ID")
    youtube_client_secret: str = Field(..., alias="YOUTUBE_CLIENT_SECRET")

settings = Settings()
