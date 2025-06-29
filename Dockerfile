FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    pkg-config \
    libssl-dev \
    ffmpeg \
    libgomp1 \
    espeak-ng \
    && rm -rf /var/lib/apt/lists/*

# Install Rust for compiling some Python packages (e.g., sudachipy, TTS)
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:$PATH"

# Set workdir
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY ./app /app

# Set env vars
ENV TTS_HOME=ds_models
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Use Uvicorn to run FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
