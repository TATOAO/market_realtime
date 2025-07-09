# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Accept build arguments for mirrors
ARG APT_MIRROR=""
ARG APT_SECURITY_MIRROR=""
ARG PYPI_INDEX_URL=""
ARG PYPI_TRUSTED_HOST=""

# Configure APT mirrors if provided
RUN if [ -n "$APT_MIRROR" ]; then \
        echo "Configuring APT mirror: $APT_MIRROR"; \
        echo "deb http://$APT_MIRROR bookworm main" > /etc/apt/sources.list && \
        echo "deb http://$APT_MIRROR bookworm-updates main" >> /etc/apt/sources.list; \
        if [ -n "$APT_SECURITY_MIRROR" ]; then \
            echo "deb http://$APT_SECURITY_MIRROR bookworm-security main" >> /etc/apt/sources.list; \
        fi; \
    fi

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Configure git settings for better network handling
RUN git config --global http.postBuffer 524288000 && \
    git config --global http.version HTTP/1.1 && \
    git config --global http.lowSpeedLimit 0 && \
    git config --global http.lowSpeedTime 999999

# Install uv for faster package installation
RUN if [ -n "$PYPI_INDEX_URL" ]; then \
        if [ -n "$PYPI_TRUSTED_HOST" ]; then \
            pip install uv -i $PYPI_INDEX_URL --trusted-host $PYPI_TRUSTED_HOST; \
        else \
            pip install uv -i $PYPI_INDEX_URL; \
        fi; \
    else \
        pip install uv; \
    fi

# Copy requirements and install Python dependencies using uv
COPY requirement.txt .
RUN if [ -n "$PYPI_INDEX_URL" ]; then \
        if [ -n "$PYPI_TRUSTED_HOST" ]; then \
            uv pip install --system -r requirement.txt -i $PYPI_INDEX_URL --trusted-host $PYPI_TRUSTED_HOST; \
        else \
            uv pip install --system -r requirement.txt -i $PYPI_INDEX_URL; \
        fi; \
    else \
        uv pip install --system -r requirement.txt; \
    fi

# Copy application code
COPY ../../server/ ./server/
COPY ../../apps/ ./apps/
COPY ../../schema.py .

# Create a non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

EXPOSE 8001

CMD ["uvicorn", "server.monitoring:app", "--host", "0.0.0.0", "--port", "8001", "--reload"] 