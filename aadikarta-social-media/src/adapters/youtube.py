import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import googleapiclient.http
from google.oauth2.credentials import Credentials
from src.adapters.base import SocialAdapter
from src.models.post import SocialContent
from src.config.settings import settings
import logging
import os
import requests
from pathlib import Path

logger = logging.getLogger(__name__)

class YouTubeAdapter(SocialAdapter):
    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
    API_SERVICE_NAME = "youtube"
    API_VERSION = "v3"
    TOKEN_FILE = "token.json"

    def __init__(self):
        self.youtube = self._get_authenticated_service()

    def _get_authenticated_service(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens.
        if os.path.exists(self.TOKEN_FILE):
             creds = Credentials.from_authorized_user_file(self.TOKEN_FILE, self.SCOPES)
        
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
             # Creating a client config dictionary from settings
             client_config = {
                 "installed": {
                     "client_id": settings.youtube_client_id,
                     "client_secret": settings.youtube_client_secret,
                     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                     "token_uri": "https://oauth2.googleapis.com/token",
                 }
             }
             
             flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_config(
                 client_config, self.SCOPES)
             creds = flow.run_local_server(port=0)
             
             # Save the credentials for the next run
             with open(self.TOKEN_FILE, 'w') as token:
                 token.write(creds.to_json())
                 
        return googleapiclient.discovery.build(
            self.API_SERVICE_NAME, self.API_VERSION, credentials=creds, cache_discovery=False)

    def post_text(self, content: SocialContent) -> str:
        logger.warning("YouTube does not support text-only posts (via API easily). Skipping.")
        return None

    def post_image(self, content: SocialContent) -> str:
         logger.warning("YouTube Community support is limited. Skipping image post.")
         return None

    def post_video(self, content: SocialContent) -> str:
        # Download video first
        video_path = "temp_video.mp4"
        logger.info(f"Downloading video from {content.video_url}...")
        response = requests.get(content.video_url, stream=True)
        with open(video_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)

        try:
            body = {
                "snippet": {
                    "title": content.text.split('\n')[0][:100], # Title is first line
                    "description": content.full_caption,
                    "tags": content.hashtags,
                    "categoryId": "22" # People & Blogs
                },
                "status": {
                    "privacyStatus": "public" # or private
                }
            }

            media = googleapiclient.http.MediaFileUpload(
                video_path, chunksize=-1, resumable=True
            )

            request = self.youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media
            )
            
            response = request.execute()
            video_id = response['id']
            logger.info(f"Successfully uploaded to YouTube. ID: {video_id}")
            
            # Cleanup
            os.remove(video_path)
            
            return video_id

        except Exception as e:
            logger.error(f"Error uploading to YouTube: {e}")
            if os.path.exists(video_path):
                os.remove(video_path)
            raise
