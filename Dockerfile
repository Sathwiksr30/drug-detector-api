FROM python:3.12-slim
WORKDIR /app
# Install system dependencies for Pillow
RUN apt-get update && apt-get install -y \
    zlib1g-dev \
    libjpeg-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*
# Upgrade pip to avoid installation issues
RUN pip install --no-cache-dir --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu
# Install SpaCy model with multiple retries
RUN for i in 1 2 3; do python -m spacy download en_core_web_sm && break || echo "Retry $i failed, retrying..." && sleep 5; done
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]