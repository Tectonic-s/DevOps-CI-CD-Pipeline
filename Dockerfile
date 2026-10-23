FROM python:3.11-slim

# Set environment variables for Python performance & container execution
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5001 \
    HOST=0.0.0.0

# Set container working directory
WORKDIR /app

# Install lightweight system tools (curl for Docker healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a non-privileged user and group for security
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code and dataset
COPY app.py recommender.py ./
COPY data/ data/
COPY static/ static/
COPY templates/ templates/
COPY tests/ tests/

# Set file permissions to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose internal application port
EXPOSE 5001

# Health check to allow Docker and Kubernetes orchestration to monitor container health
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://127.0.0.1:5001/health || exit 1

# Launch application with Gunicorn production WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "2", "--threads", "2", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
