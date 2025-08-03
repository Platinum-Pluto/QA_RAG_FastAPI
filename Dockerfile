FROM python:3.12.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        tesseract-ocr \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender1 \
        poppler-utils && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY . /app

RUN pip install -r requirements.txt
