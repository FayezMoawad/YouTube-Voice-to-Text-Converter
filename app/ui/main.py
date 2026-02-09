import streamlit as st
import time
from pathlib import Path
import sys
from app.utils.config import TEMP_DIR

# Add root to path so we can import app modules
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

st.set_page_config(page_title="YouTube Voice-to-Text", page_icon="🎙️", layout="centered")

from app.core.orchestrator import Orchestrator

# Initialize Orchestrator in Session State to persist across reruns
if 'orchestrator_v5' not in st.session_state:
    with st.spinner("Initializing AI Models... (This may take a moment)"):
        st.session_state.orchestrator_v5 = Orchestrator()

orchestrator = st.session_state.orchestrator_v5


st.header("🎙️ YouTube Voice-to-Text Converter")
st.markdown("Convert YouTube videos to accurate text with timestamps and speaker detection.")

# Input Section
with st.form("job_form"):
    url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...")
    
    col1, col2 = st.columns(2)
    with col1:
        language = st.selectbox("Language", ["en", "es", "fr", "de", "it", "ja", "zh", "ru"], index=0)
    with col2:
        model_size = st.selectbox("Model Size", ["tiny", "base", "small", "medium"], index=2, help="Larger models are more accurate but slower.")
    
    col_opt1, col_opt2 = st.columns(2)
    with col_opt1:
        include_timestamps = st.checkbox("Include Timestamps", value=True)
    with col_opt2:
        include_speakers = st.checkbox("Include Speaker Labels", value=True)
    
    # Advanced Options for Cookies
    with st.expander("Advanced Options (Fix 403 Forbidden Error)"):
        st.markdown("Upload a `cookies.txt` file if you encounter valid YouTube URL errors (403 Forbidden).")
        uploaded_cookies = st.file_uploader("Upload cookies.txt", type=["txt"], help="Use an extension like 'Get cookies.txt LOCALLY' to export your YouTube cookies.")

    submitted = st.form_submit_button("Start Transcription")

if submitted and url:
    if "youtube.com" not in url and "youtu.be" not in url:
        st.error("Please enter a valid YouTube URL.")
    else:
        # Handle Cookies
        cookies_path = None
        if uploaded_cookies is not None:
             cookies_path = TEMP_DIR / "user_cookies.txt"
             # Save uploaded file
             with open(cookies_path, "wb") as f:
                 f.write(uploaded_cookies.getbuffer())
        
        # Start Job
        job_id = orchestrator.start_job(
            url, 
            language, 
            model_size, 
            include_timestamps, 
            include_speakers,
            cookies_path=str(cookies_path) if cookies_path else None
        )
        st.session_state.current_job_id = job_id
        st.success(f"Job started! ID: {job_id}")

# Status Tracking
if 'current_job_id' in st.session_state:
    job_id = st.session_state.current_job_id
    status_placeholder = st.empty()
    progress_bar = st.progress(0)
    
    while True:
        job = orchestrator.get_job_status(job_id)
        if not job:
            st.error("Job not found.")
            break
            
        with status_placeholder.container():
            st.info(f"Status: {job.status.upper()} - {job.current_step}")
            progress_bar.progress(job.progress_percent / 100)
            
            if job.error:
                st.error(f"Error: {job.error}")
                break
                
            if job.status == "completed":
                st.success("Transcription Complete!")
                
                # Show Download Buttons
                col_d1, col_d2 = st.columns(2)
                
                if "docx" in job.artifacts:
                    with open(job.artifacts["docx"], "rb") as f:
                        col_d1.download_button("Download DOCX", f, file_name=Path(job.artifacts["docx"]).name)
                        
                if "txt" in job.artifacts:
                    with open(job.artifacts["txt"], "rb") as f:
                        col_d2.download_button("Download TXT", f, file_name=Path(job.artifacts["txt"]).name)
                
                break
        
        time.sleep(2)

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: grey;">
    Created by : <b>Fayez Mawad</b> using <b>Google Antigravity</b>
</div>
""", unsafe_allow_html=True)
