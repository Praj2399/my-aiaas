FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    pkg-config \
    libssl-dev \
    ffmpeg \
    libgomp1 \
    espeak-ng \
    && rm -rf /var/lib/apt/lists/*

# Install Rust for sudachipy and other dependencies
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app /app

# Set environment variable for TTS
ENV TTS_HOME=ds_models

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]