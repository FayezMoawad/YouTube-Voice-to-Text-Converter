import yt_dlp
import os
from pathlib import Path
from app.utils.config import TEMP_DIR, MAX_VIDEO_DURATION_SECONDS
from app.core.schemas import VideoMetadata
import logging

logger = logging.getLogger(__name__)

class IngestionAgent:
    def __init__(self):
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': str(TEMP_DIR / '%(id)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }

    def get_metadata(self, url: str) -> VideoMetadata:
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                return VideoMetadata(
                    title=info.get('title', 'Unknown'),
                    duration=info.get('duration', 0),
                    upload_date=info.get('upload_date'),
                    url=url,
                    thumbnail_url=info.get('thumbnail')
                )
        except Exception as e:
            logger.error(f"Error fetching metadata: {e}")
            raise

    def download_audio(self, url: str) -> Path:
        metadata = self.get_metadata(url)
        
        if metadata.duration > MAX_VIDEO_DURATION_SECONDS:
            raise ValueError(f"Video duration ({metadata.duration}s) exceeds limit ({MAX_VIDEO_DURATION_SECONDS}s)")

        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_id = info['id']
                # yt-dlp might save as .mp3 directly depending on postprocessor
                # We need to find the file. outtmpl was %(id)s.%(ext)s
                expected_path = TEMP_DIR / f"{video_id}.mp3"
                
                if expected_path.exists():
                    return expected_path
                else:
                     # Fallback check if it was saved with different extension before conversion?
                     # With FFmpegExtractAudio, it usually ends up as .mp3
                     raise FileNotFoundError(f"Downloaded file not found at {expected_path}")
        except Exception as e:
            logger.error(f"Error downloading audio: {e}")
            raise
