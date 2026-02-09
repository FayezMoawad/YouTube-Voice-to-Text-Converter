# Use Python 3.10-slim
FROM python:3.10-slim

# Install system dependencies (ffmpeg is crucial)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Work directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Run the app
CMD ["streamlit", "run", "app/ui/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
