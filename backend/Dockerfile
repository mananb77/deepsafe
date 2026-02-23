# DeepSafe API Service Dockerfile
# Multi-stage build for development and production

# ==============================================================================
# Base stage - Common dependencies
# ==============================================================================
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
ENV POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry

# Set working directory
WORKDIR /app

# ==============================================================================
# Dependencies stage - Install Python packages
# ==============================================================================
FROM base as dependencies

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install dependencies (without dev dependencies for production)
RUN poetry install --no-root --only main

# ==============================================================================
# Development stage - Full development environment
# ==============================================================================
FROM base as development

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install all dependencies including dev
RUN poetry install --no-root

# Copy application code
COPY . .

# Install the application
RUN poetry install --only-root

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command for development (with hot reload)
CMD ["uvicorn", "src.services.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ==============================================================================
# Production stage - Optimized for deployment
# ==============================================================================
FROM dependencies as production

# Create non-root user for security
RUN groupadd --gid 1000 deepsafe && \
    useradd --uid 1000 --gid deepsafe --shell /bin/bash --create-home deepsafe

# Copy application code
COPY --chown=deepsafe:deepsafe . .

# Install the application
RUN poetry install --only-root

# Switch to non-root user
USER deepsafe

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production command with gunicorn
CMD ["gunicorn", "src.services.api.main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--capture-output", \
     "--enable-stdio-inheritance"]
