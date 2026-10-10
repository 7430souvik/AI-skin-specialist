
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies required by PyAudio and audio processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    portaudio19-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# Install Python dependencies using the lockfile
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

# Copy application source code
COPY . .

# Make the uv-managed environment available
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Render provides the PORT environment variable
CMD ["sh", "-c", "python main.py"]
