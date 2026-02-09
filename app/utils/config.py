import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMP_DIR = BASE_DIR / "temp"
OUTPUT_DIR = BASE_DIR / "output"

# Ensure dirs exist
TEMP_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Settings
MAX_VIDEO_DURATION_SECONDS = 4 * 3600  # 4 hours
CHUNK_SIZE_SECONDS = 600  # 10 minutes
CHUNK_OVERLAP_SECONDS = 5
SUPPORTED_LANGUAGES = ["en", "es", "fr", "de", "it", "pt", "nl", "ja", "zh", "ru"]

# Model Settings
WHISPER_MODEL_SIZE = "medium"  # 'tiny', 'base', 'small', 'medium', 'large-v2'
COMPUTE_TYPE = "int8" # 'float16' for GPU, 'int8' for CPU efficiency

# Retry Logic
MAX_RETRIES = 3
RETRY_DELAY = 5
