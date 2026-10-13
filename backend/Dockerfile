# Stage 1: install runtime dependencies into a virtualenv
FROM python:3.12-slim AS build

ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
RUN python -m venv /venv
COPY backend/requirements.txt /tmp/requirements.txt
# pip/setuptools are only needed to install; keep the bytecode pip compiles (faster startup)
RUN /venv/bin/pip install -r /tmp/requirements.txt \
    && /venv/bin/pip uninstall -y pip setuptools

# Stage 2: runtime image with only the interpreter, the virtualenv and the app
FROM python:3.12-slim

ENV PATH=/venv/bin:$PATH \
    PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create a non-root user and the directories mounted as volumes
RUN groupadd -r appgroup && useradd -r -g appgroup appuser && \
    mkdir -p /app/data /app/uploads /app/backups && \
    chown -R appuser:appgroup /app

COPY --from=build /venv /venv
COPY --chown=appuser:appgroup backend /app/backend
# Precompile the app as well, since the runtime user doesn't write bytecode
RUN python -m compileall -q /app/backend

WORKDIR /app
USER appuser

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
