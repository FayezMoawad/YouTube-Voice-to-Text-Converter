import sys
from pathlib import Path

# Add root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

def test_imports():
    print("Testing imports...")
    try:
        from app.utils.config import TEMP_DIR
        print(f"Config loaded. TEMP_DIR: {TEMP_DIR}")
        
        from app.utils.logger import setup_logger
        logger = setup_logger("test")
        logger.info("Logger working.")
        
        from app.core.schemas import JobStatus
        print("Schemas loaded.")
        
        from app.agents.ingestion import IngestionAgent
        print("IngestionAgent loaded.")
        
        from app.agents.transcription import TranscriptionAgent
        print("TranscriptionAgent loaded.")
        
        from app.agents.formatting import FormattingAgent
        print("FormattingAgent loaded.")
        
        from app.core.orchestrator import Orchestrator
        print("Orchestrator loaded.")
        
        print("ALL IMPORTS SUCCESSFUL")
    except Exception as e:
        print(f"IMPORT ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_imports()
