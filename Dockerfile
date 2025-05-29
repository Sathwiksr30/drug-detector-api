FROM python:3.12-slim
WORKDIR /app
# Install system dependencies for Pillow, OpenCV, and others
RUN apt-get update && apt-get install -y \
    zlib1g-dev \
    libjpeg-dev \
    libpng-dev \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*
# Upgrade pip to avoid installation issues
RUN pip install --no-cache-dir --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu
# Install SpaCy model with error handling
RUN python -m spacy download en_core_web_sm || (echo "SpaCy model download failed, retrying..." && python -m spacy download en_core_web_sm)
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]