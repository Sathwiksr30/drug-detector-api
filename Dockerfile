FROM python:3.12
WORKDIR /app
RUN pip install --no-cache-dir --upgrade pip
COPY pre_install.py .
RUN python pre_install.py
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu
COPY install_spacy_model.py .
RUN python install_spacy_model.py
ENV OPENCV_PYTHON_HEADLESS=1
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]