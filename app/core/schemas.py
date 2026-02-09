from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Word(BaseModel):
    word: str
    start: float
    end: float
    confidence: float

class Segment(BaseModel):
    segment_id: int
    start_time: float
    end_time: float
    text: str
    speaker: str = "SPEAKER_00"
    confidence: float
    words: List[Word] = []

class VideoMetadata(BaseModel):
    title: str
    duration: float
    upload_date: Optional[str] = None
    url: str
    thumbnail_url: Optional[str] = None

class Transcript(BaseModel):
    job_id: str
    segments: List[Segment]
    metadata: VideoMetadata

class JobStatus(BaseModel):
    job_id: str
    status: str = "pending" # pending, processing, completed, failed
    progress_percent: int = 0
    current_step: str = "initialized"
    error: Optional[str] = None
    artifacts: dict = {} # {"docx": "path", "txt": "path"}
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
