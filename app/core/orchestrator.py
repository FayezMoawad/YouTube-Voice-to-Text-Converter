import uuid
import logging
from app.agents.ingestion import IngestionAgent
from app.agents.transcription import TranscriptionAgent
from app.agents.formatting import FormattingAgent
from app.core.schemas import JobStatus, Transcript, VideoMetadata
from pathlib import Path
import threading

logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self):
        self.jobs = {} # In-memory job store
        self.ingestion = IngestionAgent()
        self.transcription = TranscriptionAgent() # Model loads here
        self.formatting = FormattingAgent()

    def start_job(self, url: str, language: str = None, model_size: str = "medium", include_timestamps: bool = True, include_speakers: bool = True, cookies_path: str = None) -> str:
        job_id = str(uuid.uuid4())
        self.jobs[job_id] = JobStatus(job_id=job_id, status="initialized")
        
        # Start processing in a background thread
        thread = threading.Thread(target=self._process_job, args=(job_id, url, language, model_size, include_timestamps, include_speakers, cookies_path))
        thread.start()
        
        return job_id

    def get_job_status(self, job_id: str) -> JobStatus:
        return self.jobs.get(job_id)

    def _process_job(self, job_id: str, url: str, language: str, model_size: str, include_timestamps: bool, include_speakers: bool, cookies_path: str = None):
        job = self.jobs[job_id]
        try:
            # 1. Ingestion
            job.status = "processing"
            job.current_step = "fetching_audio"
            job.progress_percent = 10
            logger.info(f"Job {job_id}: Fetching audio from {url}")
            
            # Convert cookies_path to Path object if it exists
            cookie_file = Path(cookies_path) if cookies_path else None
            
            # Get metadata first
            metadata: VideoMetadata = self.ingestion.get_metadata(url, cookie_file=cookie_file)
            
            # Download audio
            audio_path = self.ingestion.download_audio(url, cookie_file=cookie_file)
            job.progress_percent = 30
            
            # 2. Transcription
            job.current_step = "transcribing"
            logger.info(f"Job {job_id}: Transcribing with {model_size} model...")
            segments = self.transcription.transcribe(audio_path, language=language, model_size=model_size)
            job.progress_percent = 80
            
            transcript = Transcript(
                job_id=job_id,
                segments=segments,
                metadata=metadata
            )
            
            # 3. Formatting
            job.current_step = "formatting"
            logger.info(f"Job {job_id}: Formatting...")
            docx_path = self.formatting.format_docx(transcript, include_timestamps=include_timestamps, include_speakers=include_speakers)
            txt_path = self.formatting.format_txt(transcript, include_timestamps=include_timestamps, include_speakers=include_speakers)
            
            job.artifacts = {
                "docx": str(docx_path),
                "txt": str(txt_path)
            }
            
            # Cleanup
            if audio_path.exists():
                audio_path.unlink()
            
            job.status = "completed"
            job.progress_percent = 100
            job.current_step = "done"
            logger.info(f"Job {job_id}: Completed successfully.")

        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}")
            job.status = "failed"
            job.error = str(e)
