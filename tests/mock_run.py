from unittest.mock import MagicMock
import sys
from pathlib import Path

# Add root to path
base_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(base_dir))

from app.core.orchestrator import Orchestrator
from app.core.schemas import Segment, VideoMetadata

def test_mock_run():
    print("Initializing Mock Orchestrator...")
    orchestrator = Orchestrator()
    
    # Mock Ingestion
    orchestrator.ingestion.get_metadata = MagicMock(return_value=VideoMetadata(
        title="Mock Video",
        duration=60,
        upload_date="2023-01-01",
        url="http://mock.url"
    ))
    orchestrator.ingestion.download_audio = MagicMock(return_value=Path(base_dir / "temp/mock_audio.mp3"))
    
    # Create a dummy file for the "downloaded" audio so FileExists checks pass
    (base_dir / "temp/mock_audio.mp3").touch()
    
    # Mock Transcription
    orchestrator.transcription.transcribe = MagicMock(return_value=[
        Segment(segment_id=1, start_time=0.0, end_time=5.0, text="Hello world.", confidence=0.9),
        Segment(segment_id=2, start_time=5.0, end_time=10.0, text="This is a test.", confidence=0.95),
    ])
    
    # Start Job
    print("Starting Job...")
    job_id = orchestrator.start_job("http://mock.url")
    
    # Wait for completion
    import time
    max_wait = 10
    start = time.time()
    
    while time.time() - start < max_wait:
        job = orchestrator.get_job_status(job_id)
        if job.status in ["completed", "failed"]:
            break
        time.sleep(1)
        
    print(f"Job Status: {job.status}")
    if job.status == "completed":
        print(f"Artifacts: {job.artifacts}")
    else:
        print(f"Error: {job.error}")

if __name__ == "__main__":
    test_mock_run()
