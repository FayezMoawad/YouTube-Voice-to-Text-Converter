from faster_whisper import WhisperModel
from pathlib import Path
from app.utils.config import WHISPER_MODEL_SIZE, COMPUTE_TYPE
from app.core.schemas import Segment, Word
import logging

logger = logging.getLogger(__name__)

class TranscriptionAgent:
    def __init__(self):
        self.current_model_size = None
        self.model = None

    def load_model(self, model_size: str):
        if self.model and self.current_model_size == model_size:
            return  # Already loaded

        try:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Loading Whisper model '{model_size}' on {device} with {COMPUTE_TYPE}...")
            
            # Unload previous model to free memory if needed (Python GC handles it mostly, but explicit delete helps)
            if self.model:
                del self.model
            
            self.model = WhisperModel(model_size, device=device, compute_type=COMPUTE_TYPE)
            self.current_model_size = model_size
            logger.info(f"Model '{model_size}' loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise

    def transcribe(self, audio_path: Path, language: str = None, model_size: str = WHISPER_MODEL_SIZE) -> list[Segment]:
        self.load_model(model_size)
        
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        try:
            logger.info(f"Starting transcription for {audio_path.name}...")
            segments, info = self.model.transcribe(
                str(audio_path), 
                language=language,
                beam_size=5,
                word_timestamps=True # We need word timestamps for better granularity
            )

            result_segments = []
            segment_id_counter = 1
            
            for segment in segments:
                # Convert faster_whisper segment to our Schema
                words = []
                if segment.words:
                    for w in segment.words:
                        words.append(Word(
                            word=w.word,
                            start=w.start,
                            end=w.end,
                            confidence=w.probability
                        ))

                result_segments.append(Segment(
                    segment_id=segment_id_counter,
                    start_time=segment.start,
                    end_time=segment.end,
                    text=segment.text.strip(),
                    confidence=segment.avg_logprob, # Approximation or use another metric
                    words=words
                ))
                segment_id_counter += 1
            
            logger.info(f"Transcription complete. Detected language: {info.language}")
            return result_segments
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise
