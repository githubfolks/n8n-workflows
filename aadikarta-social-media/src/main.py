import argparse
import logging
import sys
from src.core.content_generator import ContentGenerator
from src.core.video_creator import VideoCreator
from src.adapters.facebook import FacebookAdapter
from src.adapters.instagram import InstagramAdapter
from src.adapters.youtube import YouTubeAdapter
from src.models.post import ContentRequest

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Social Media Automation Engine")
    parser.add_argument("topic", help="The topic for the social media post")
    parser.add_argument("--platforms", nargs="+", default=["facebook", "instagram"], choices=["facebook", "instagram", "youtube"], help="Target platforms")
    parser.add_argument("--video", action="store_true", help="Generate and post a video")
    parser.add_argument("--dry-run", action="store_true", help="Generate content but do not post")

    args = parser.parse_args()

    try:
        # Step 1: Generate Content
        logger.info(f"Generating content for topic: {args.topic}")
        generator = ContentGenerator()
        content = generator.generate_content(args.topic)
        
        logger.info("Generated Text Content:")
        logger.info(content.full_caption)

        # Step 2: Generate Media (Image or Video)
        if args.video:
            logger.info("Generating Video via Creatomate...")
            video_creator = VideoCreator()
            # Assuming template has 'text_content' and 'image_1' slots. 
            # We might want to generate an image to put IN the video first.
            image_url_for_video = generator.generate_image(content.image_url or f"Visual for {args.topic}")
            
            modifications = {
                "Text-1": content.text, # Update based on actual template
                "Image-1": image_url_for_video
            }
            video_url = video_creator.create_video(modifications)
            content.video_url = video_url
            logger.info(f"Video generated: {video_url}")

        if args.image and not args.video: # Prefer video if both selected? Or do both? Let's check logic.
            # If video is NOT selected, or if we want an image post specifically.
            # Current logic: If video flag is set, we do video. If image flag is set (default), we do image.
            # The user might want a video post for YT/IG Reels and Image for FB/Twitter.
            if not content.image_url:
                logger.info("Generating Image via DALL-E 3...")
                prompt = content.image_prompt or f"High quality, photorealistic image representing: {args.topic}"
                content.image_url = generator.generate_image(prompt)
                logger.info(f"Image generated: {content.image_url}")

        if args.dry_run:
            logger.info("Dry run complete. Exiting.")
            return

        # Step 3: Publish
        logger.info(f"Publishing to {args.platforms}...")
        
        results = {}
        
        for platform in args.platforms:
            adapter = None
            try:
                if platform == "facebook":
                    adapter = FacebookAdapter()
                elif platform == "instagram":
                    adapter = InstagramAdapter()
                elif platform == "youtube":
                    adapter = YouTubeAdapter()
                
                if adapter:
                    if args.video and platform in ["youtube", "instagram", "facebook"]:
                         # Prefer video for these if available
                         post_id = adapter.post_video(content)
                    elif content.image_url:
                         post_id = adapter.post_image(content)
                    else:
                         post_id = adapter.post_text(content)
                    
                    if post_id:
                        results[platform] = "Success"
                    else:
                        results[platform] = "Skipped/Failed"
            except Exception as e:
                logger.error(f"Error publishing to {platform}: {e}")
                results[platform] = f"Error: {str(e)}"

        logger.info("Publishing complete.")
        logger.info(results)

    except Exception as e:
        logger.critical(f"Workflow failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
