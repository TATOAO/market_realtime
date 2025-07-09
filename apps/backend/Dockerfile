FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY ../../requirement.txt .
RUN pip install --no-cache-dir -r requirement.txt
RUN pip install fastapi uvicorn sqlalchemy psycopg2-binary alembic

# Copy application code
COPY ../../server/ ./server/
COPY ../../apps/ ./apps/
COPY ../../schema.py .

# Create a non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

EXPOSE 8000

CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 