from openai import OpenAI
from app.core.config import settings
import logging
import asyncio
import json

logger = logging.getLogger(__name__)

class StoryService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

    async def generate_story(self, topic: str) -> str:
        """
        Takes a topic and generates a short 30-second video script consisting of exactly 3 sentences/clauses.
        """
        prompt = f"""
        You are an intelligent and factual knowledge assistant.
        The user has provided the following topic or question: "{topic}".
        
        CRITICAL RULES:
        1. Write a plain, concise, and factual answer to the topic/question.
        2. DO NOT include any structural markers, prefixes, timestamps (like [0-10s]), or metadata.
        3. The response should flow naturally as a single short paragraph or a few brief sentences.
        4. The length must be appropriate to eventually be spoken in a 30-second video (around 60-75 words).
        
        Return ONLY the finalized plain text answer. No other commentary.
        """
        
        loop = asyncio.get_event_loop()
        try:
            return await loop.run_in_executor(None, self._run_openai_chat, prompt)
        except Exception as e:
            logger.error(f"Error generating story: {e}")
            raise

    async def generate_scenes(self, story_text: str) -> list[dict]:
        """
        Parses a generated story script into structural scenes (id and description).
        """
        prompt = f"""
        You are a video producer specializing in Indian culture, Vedic astrology, and Indian mythology.
        Here is a short script/informative text:
        
        {story_text}
        
        Convert this text into a structured JSON array of 3 sequential visual scenes that could accompany this text in a 30-second video.
        Each scene should represent roughly 10 seconds of visual content.
        
        CRITICAL RULE for scenes:
        All visual descriptions MUST heavily incorporate elements of Vedic astrology (Jyotish), Indian mythology (e.g., deities, epics), or rich Indian cultural aesthetics (e.g., temples, traditional art, attire, spiritual symbols).
        
        Return ONLY valid JSON in this exact structure:
        [
            {{ "id": 1, "description": "Visual details for what is shown on screen during the first 10 seconds..." }},
            {{ "id": 2, "description": "Visual details for what is shown on screen during the next 10 seconds..." }},
            {{ "id": 3, "description": "Visual details for what is shown on screen during the final 10 seconds..." }}
        ]
        """
        
        loop = asyncio.get_event_loop()
        try:
            json_text = await loop.run_in_executor(None, self._run_openai_json, prompt)
            data = json.loads(json_text)
            # OpenAI sometimes wraps the array in an object like {"scenes": [...]}
            if isinstance(data, dict):
                # Try to find the array value
                for key, value in data.items():
                    if isinstance(value, list):
                        return value
                # Fallback if no list is found inside the dict
                return [data]
            return data
        except Exception as e:
            logger.error(f"Error generating scenes: {e}")
            raise
            
    def _run_openai_chat(self, prompt: str) -> str:
        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[
                {"role": "system", "content": "You are a creative scriptwriter."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()

    def _run_openai_json(self, prompt: str) -> str:
        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Provide output strictly in JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            response_format={"type": "json_object" if "{" in prompt else "text"}
        )
        content = response.choices[0].message.content.strip()
        # Clean markdown code blocks if present
        return content.replace("```json", "").replace("```", "").strip()
