FROM python:3.12-slim

WORKDIR /app

# Install system deps for PDF parsing
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpoppler-cpp-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app
ENV OUTPUT_DIR=/app/outputs

VOLUME ["/app/outputs"]

ENTRYPOINT ["python", "scripts/run_assessment.py"]
