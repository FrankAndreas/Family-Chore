FROM python:3.12-slim

WORKDIR /app

# Install system dependencies if needed (none strictly for basic python apps, but good practice)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend directory to /app/backend
COPY backend /app/backend

# Set pythonpath to include /app
ENV PYTHONPATH=/app
# Create a non-root user and set permissions
RUN groupadd -r appgroup && useradd -r -g appgroup appuser && \
    mkdir -p /app/data && \
    chown -R appuser:appgroup /app

USER appuser

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
