FROM python:3.12
WORKDIR /app
# Install system dependencies
RUN apt-get update && apt-get install -y \
    zlib1g-dev \
    libjpeg-dev \
    libpng-dev \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir --upgrade pip
# Run pre-install to ensure opencv-python-headless
COPY pre_install.py .
RUN python pre_install.py
# Copy debug output
COPY installed_packages.txt .
# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu
# Install SpaCy model
COPY install_spacy_model.py .
RUN python install_spacy_model.py
# Set environment variable
ENV OPENCV_PYTHON_HEADLESS=1
# Copy application
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]