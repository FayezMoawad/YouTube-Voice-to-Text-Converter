import os
import sys
from pathlib import Path
import subprocess

def main():
    # Ensure dependencies are installed
    # check_dependencies() # Optional
    
    # Run Streamlit
    script_path = Path("app/ui/main.py").resolve()
    print(f"Starting YouTube Voice-to-Text App...")
    print(f"Running: streamlit run {script_path}")
    
    try:
        subprocess.run(["streamlit", "run", str(script_path)], check=True)
    except KeyboardInterrupt:
        print("\nStopping application...")

if __name__ == "__main__":
    main()
