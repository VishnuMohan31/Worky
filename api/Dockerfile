# =========================
# Use Python 3.11 slim image
# =========================
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app ./app

# =========================
# Copy Alembic configuration and migrations
# =========================
# Ensure env.py exists locally in alembic/ before building
COPY alembic.ini ./ 
COPY alembic ./alembic

# Verify env.py exists (optional debug)
RUN test -f alembic/env.py

# Create logs and uploads directories
RUN mkdir -p /app/logs /app/uploads && chmod 777 /app/logs /app/uploads

# Create non-root user
RUN useradd -m -u 1000 worky && chown -R worky:worky /app

# Switch to non-root user
USER worky

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
