from openai import OpenAI
from app.core.config import settings
import logging
import asyncio

logger = logging.getLogger(__name__)

class ContentService:
    def __init__(self):
        # OpenAI Client (Global)
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # LM Studio Client (Local)
        self.lm_studio_client = OpenAI(
            base_url=settings.LM_STUDIO_BASE_URL,
            api_key="lm-studio"
        )
        
        self.provider = settings.LLM_PROVIDER
        
        self.prompt_template = """
        You are a professional social media manager. Create an engaging post about: "{topic}".
        
        Return the response in the following format:
        Title: <A catchy title>
        Content: <The main post content, engaging and suitable for Instagram/Facebook/Twitter>
        Hashtags: <List of 5-10 relevant hashtags, comma separated>
        Image Prompt: <A detailed description for an AI image generator to create a visual for this post>
        """

    async def generate_text(self, topic: str, tone: str = "professional", platform: str = "generic") -> dict:
        """
        Generates structured social media content based on a topic, tone, and platform.
        """
        prompt = self._build_prompt(topic, tone, platform)
        
        # Async wrapper for synchronous calls
        loop = asyncio.get_event_loop()
        
        try:
            if self.provider == "lm_studio":
                return await loop.run_in_executor(None, self._generate_lm_studio, prompt)
            else:
                # Default to OpenAI
                return await loop.run_in_executor(None, self._generate_openai, prompt)
                
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            raise

    def _build_prompt(self, topic: str, tone: str, platform: str) -> str:
        return f"""
        Act as a viral social media expert. Create content for:
        Topic: {topic}
        Tone: {tone}
        Platform: {platform}

        Requirements:
        1. Caption: Engaging, uses hooks, suitable for {platform}.
        2. Hashtags: 5-10 high-traffic, relevant tags.
        3. Image Prompt: Detailed, cinematic description for AI image generation.
        4. Video Script: A short 15-30s script for a Reel/Short (start with a visual hook).

        Output MUST be valid JSON only, with this structure:
        {{
            "caption": "string",
            "hashtags": ["tag1", "tag2"],
            "image_prompt": "string",
            "video_script": "string"
        }}
        """


    def _generate_openai(self, prompt: str) -> dict:
        logger.info("Generating via OpenAI")
        return self._run_openai_chat(self.openai_client, "gpt-3.5-turbo-0125", prompt)

    def _generate_lm_studio(self, prompt: str) -> dict:
        logger.info(f"Generating via LM Studio at {settings.LM_STUDIO_BASE_URL}")
        # LM Studio usually ignores model name if only one model is loaded, but verification is good practice
        return self._run_openai_chat(self.lm_studio_client, "local-model", prompt)

    def _run_openai_chat(self, client: OpenAI, model: str, prompt: str) -> dict:
        response = client.chat.completions.create(
            model=model, 
            messages=[
                {"role": "system", "content": "You are a creative social media assistant. Output strictly in JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        return self._parse_json_response(response.choices[0].message.content)

    def _parse_json_response(self, text: str) -> dict:
        import json
        try:
            # Clean possible markdown code blocks
            clean_text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}. Text: {text}")
            # Fallback or raise
            raise ValueError("LLM did not return valid JSON")
