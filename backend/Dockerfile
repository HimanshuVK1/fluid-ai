# Stage 1: Build dependencies
FROM python:3.11-alpine AS builder

WORKDIR /app

# Upgrade pip and install requirements into a virtual environment
RUN pip install --no-cache-dir --upgrade pip

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Final lightweight image
FROM python:3.11-alpine

# Configure secure and optimized Python environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Copy virtual environment containing all dependencies from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy only the required application code
COPY main.py .

# Create a non-privileged system user for runtime security (Alpine native)
RUN adduser -D appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Start FastAPI application using the virtual environment's uvicorn package
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
