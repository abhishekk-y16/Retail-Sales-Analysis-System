# Use a slim Python base image to reduce attack surface and image size
FROM python:3.9-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Define the working directory within the container
WORKDIR /app

# Install critical OS-level dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the core project directories
COPY src/ ./src/
COPY dashboard/ ./dashboard/
COPY data/01_raw/ ./data/01_raw/
COPY .streamlit/ ./.streamlit/

# Expose the default Streamlit network port
EXPOSE 8501

# Health check to monitor container viability
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Execute the Streamlit application listening on all network interfaces
ENTRYPOINT ["streamlit", "run", "dashboard/app.py", \
    "--server.port=8501", \
    "--server.address=0.0.0.0", \
    "--server.headless=true"]
