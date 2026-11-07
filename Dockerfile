# Use an official Python base image (3.11 for high compatibility)
FROM python:3.11-slim

# Install system dependencies (OCR, Hebrew language pack, Poppler utils)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    tesseract-ocr \
    tesseract-ocr-heb \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency definition and install packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Default execution command
CMD ["python", "main.py"]