import ffmpeg
import logging
import os
from typing import List
from pathlib import Path

logger = logging.getLogger(__name__)

class VideoEngine:
    def __init__(self, output_dir: str = "/tmp"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        # Fonts would be loaded here for text overlay, skipping for MVP simplicity or using system font

    def create_video(self, image_paths: List[str], audio_path: str = None, captions: List[str] = None, duration_per_image: float = 3.0) -> str:
        """
        Creates a slideshow video from images with crossfade transitions and optional audio.
        Returns the path to the generated output file.
        """
        try:
            output_filename = self.output_dir / "output.mp4"
            
            # 1. Prepare Inputs
            # Resize all images to 1080x1920 (9:16) and create streams
            # This complex filter chain mimics a slideshow with crossfades.
            # For MVP robustness, we might just concat them. Crossfade in pure ffmpeg cli is tricky dynamic.
            # Using a simpler concat approach for v1.
            
            # Create a file list for concat demuxer (simplest efficient way)
            # BUT concat demuxer requires same codecs/dims. We must ensure images are sized right.
            # Better: Use image2pipe or simple filter complex.
            
            # Let's use the 'zoompan' filter effect for dynamic motion (Ken Burns) + concat.
            
            # Simplified approach: create a list of input streams
            streams = []
            for img_path in image_paths:
                # Loop image for duration
                streams.append(
                    ffmpeg.input(img_path, loop=1, t=duration_per_image)
                    .filter('scale', 1080, 1920, force_original_aspect_ratio='decrease')
                    .filter('pad', 1080, 1920, '(ow-iw)/2', '(oh-ih)/2')
                    .filter('setsar', 1)
                )

            # Concat streams
            joined = ffmpeg.concat(*streams, v=1, a=0).node
            video = joined[0]

            if captions and len(captions) > 0:
                # Basic text overlay
                # You'd normally want to split this across frames, but for simplicity
                # we'll place the first caption at the bottom of the screen.
                safe_text = captions[0].replace("'", "\'")
                video = video.filter(
                    'drawtext',
                    text=safe_text,
                    fontcolor='white',
                    fontsize=60,
                    box=1,
                    boxcolor='black@0.5',
                    boxborderw=10,
                    x='(w-text_w)/2',
                    y='(h-text_h)-100'
                )

            # Add Audio if present, otherwise generate silent audio
            # Facebook requires an audio stream in uploaded videos
            total_duration = duration_per_image * len(image_paths)
            if audio_path:
                audio = ffmpeg.input(audio_path)
            else:
                # Generate silent audio track matching video duration
                audio = ffmpeg.input('anullsrc', f='lavfi', t=total_duration)

            output = ffmpeg.output(
                video, audio, str(output_filename),
                vcodec='libx264', acodec='aac', pix_fmt='yuv420p',
                shortest=None,
                **{'movflags': '+faststart'}
            )

            # Run
            logger.info("Running FFmpeg render...")
            output.run(overwrite_output=True)
            
            return str(output_filename)

        except ffmpeg.Error as e:
            logger.error(f"FFmpeg error: {e.stderr.decode('utf8') if e.stderr else str(e)}")
            raise
        except Exception as e:
            logger.error(f"Video generation error: {e}")
            raise
