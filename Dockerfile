# 1. Build dependencies
FROM python:3.12-slim AS builder

WORKDIR /build

RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY app/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# 2. Production runtime
FROM python:3.12-slim AS runtime

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Use virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Python runtime configuration
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create non-root user
RUN groupadd --system appgroup && \
    useradd --system --gid appgroup appuser

# Copy application source code
COPY --chown=appuser:appgroup app/ .

# Switch to non-root user
USER appuser

# Expose application port
EXPOSE 5000

# Start application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "--timeout", "30", "app:app"]
