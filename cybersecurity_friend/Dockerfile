# Use official Python lightweight image
FROM python:3.10-slim

# Install system dependencies (needed for FAISS and other libs)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Hugging Face Spaces run safely under a non-root user. Let's set it up:
RUN useradd -m -u 1000 user
USER user

# Set up environment variables for the user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Set the working directory
WORKDIR $HOME/app

# Copy requirements and install them
COPY --chown=user:user requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy the rest of the application
COPY --chown=user:user . .

# Expose the default Hugging Face Port
EXPOSE 7860
ENV PORT=7860

# Command to run our FastAPI backend (With gunicorn for better performance here)
CMD ["gunicorn", "api:app", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:7860", "--timeout", "120"]
