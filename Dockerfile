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
# Create non-root user
RUN useradd -m -u 1000 appuser
# Set up venv
RUN python -m venv /home/adminuser/venv
RUN chown -R appuser:appuser /home/adminuser/venv
# Copy and run pre-install
COPY pre_install.py .
RUN /home/adminuser/venv/bin/python pre_install.py
# Install dependencies
COPY requirements.txt .
RUN /home/adminuser/venv/bin/pip install --no-cache-dir -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu
# Install SpaCy model as root
COPY install_spacy_model.py .
RUN /home/adminuser/venv/bin/python install_spacy_model.py
# Copy application
COPY . .
# Switch to non-root user
USER appuser
EXPOSE 8000
CMD ["/home/adminuser/venv/bin/uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]