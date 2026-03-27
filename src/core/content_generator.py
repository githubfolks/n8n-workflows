from openai import OpenAI
from src.config.settings import settings
from src.models.post import SocialContent
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ContentGenerator:
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.openai_api_key)
        
        # Load prompt template
        template_path = Path(__file__).parent / "prompt_template.txt"
        if template_path.exists():
            self.prompt_template = template_path.read_text()
        else:
            self.prompt_template = """
            You are a professional social media manager. Create an engaging post about: "{topic}".
        
            Return the response in the following format:
            Title: <A catchy title>
            Content: <The main post content, engaging and suitable for Instagram/Facebook>
            Hashtags: <List of 5-10 relevant hashtags, comma separated>
            Image Prompt: <A detailed description for an AI image generator to create a visual for this post>
            """

    def generate_content(self, topic: str) -> SocialContent:
        """
        Generates social media content based on a topic using OpenAI or Ollama.
        """
        prompt = self.prompt_template.replace("{topic}", topic)

        try:
            logger.info("Generating text using OpenAI (gpt-3.5-turbo)...")
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a creative social media assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            content_text = response.choices[0].message.content
            
            return self._parse_response(content_text)

        except Exception as e:
            logger.error(f"Error generating content: {e}")
            raise

    def _parse_response(self, text: str) -> SocialContent:
        """
        Parses the raw text response from OpenAI into a structured SocialContent object.
        """
        lines = text.strip().split('\n')
        title = ""
        body = ""
        hashtags = []
        image_prompt = ""

        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith("Title:"):
                title = line.replace("Title:", "").strip()
            elif line.startswith("Content:"):
                current_section = "content"
                body = line.replace("Content:", "").strip()
            elif line.startswith("Hashtags:"):
                current_section = "hashtags"
                tags = line.replace("Hashtags:", "").strip()
                hashtags = [t.strip().replace("#", "") for t in tags.split(',')]
            elif line.startswith("Image Prompt:"):
                current_section = "image_prompt"
                image_prompt = line.replace("Image Prompt:", "").strip()
            elif current_section == "content":
                body += "\n" + line
        
        # Fallback if structure is messy
        if not body:
            body = text

        return SocialContent(
            text=f"{title}\n\n{body}",
            hashtags=hashtags,
            image_prompt=image_prompt,
            image_url=None 
        )

    def generate_image(self, prompt: str) -> str:
        """
        Generates an image using DALL-E 3 based on the prompt.
        Always uses OpenAI as Ollama does not support image generation natively yet.
        """
        try:
            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            return response.data[0].url
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return None
