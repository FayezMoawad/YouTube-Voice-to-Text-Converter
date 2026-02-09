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
            'format': 'best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': str(TEMP_DIR / '%(id)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }

    def get_metadata(self, url: str, cookie_file: Path = None) -> VideoMetadata:
        try:
            opts = {'quiet': True}
            
            if cookie_file and cookie_file.exists():
                logger.info(f"Using cookie file at: {cookie_file}")
                # Basic validation: check if it looks like a Netscape cookie file
                try:
                    with open(cookie_file, 'r') as f:
                        header = f.readline()
                        if not header.startswith("# Netscape") and not header.startswith("# HTTP Cookie"):
                            logger.warning(f"Cookie file {cookie_file} does not look like a Netscape format file. Header: {header.strip()}")
                except Exception as ex:
                    logger.warning(f"Could not read cookie file to validate header: {ex}")
                    
                opts['cookiefile'] = str(cookie_file)
                
            with yt_dlp.YoutubeDL(opts) as ydl:
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

    def download_audio(self, url: str, cookie_file: Path = None) -> Path:
        # We pass cookie_file to get_metadata if needed, though usually metadata doesn't require it as strictly as download
        # But for 403s, even metadata might fail, so let's pass it.
        metadata = self.get_metadata(url, cookie_file=cookie_file)
        
        if metadata.duration > MAX_VIDEO_DURATION_SECONDS:
            raise ValueError(f"Video duration ({metadata.duration}s) exceeds limit ({MAX_VIDEO_DURATION_SECONDS}s)")

        try:
            # Create a localized copy of options to add cookiefile
            opts = self.ydl_opts.copy()
            if cookie_file and cookie_file.exists():
                opts['cookiefile'] = str(cookie_file)

            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_id = info['id']
                # yt-dlp might save as .mp3 directly depending on postprocessor
                # We need to find the file. outtmpl was %(id)s.%(ext)s
                expected_path = TEMP_DIR / f"{video_id}.mp3"
                
                if expected_path.exists():
                    return expected_path
                else:
                     # Check if it was saved as webm or m4a before conversion (unlikely with just extract audio but possible)
                     # For now, strict check on mp3 as per config
                     if not expected_path.exists():
                         # Try finding any file with that ID in temp
                         potential_files = list(TEMP_DIR.glob(f"{video_id}.*"))
                         if potential_files:
                             return potential_files[0]
                     
                     raise FileNotFoundError(f"Downloaded file not found at {expected_path}")
        except Exception as e:
            logger.error(f"Error downloading audio: {e}")
            raise
