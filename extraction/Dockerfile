FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY extraction/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY extraction/src/ ./src/
COPY adapters/ ./adapters/
COPY extraction/fixtures/ ./fixtures/

ENV PYTHONPATH=/app/src:/app/adapters/src

CMD ["python", "src/seed_docker.py"]
