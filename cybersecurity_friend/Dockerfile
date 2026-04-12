# Use official Python lightweight image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (needed for FAISS and other libs)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose ports for both services
EXPOSE 8000
EXPOSE 8501

# Default environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# The actual command will be provided by the cloud platform
# or via 'docker run ... uvicorn api:app'
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
