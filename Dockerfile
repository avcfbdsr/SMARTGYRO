FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Google Cloud CLI
RUN curl https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-455.0.0-linux-x86_64.tar.gz -o gcloud.tar.gz && \
    tar -xf gcloud.tar.gz && \
    ./google-cloud-sdk/install.sh --quiet --path-update=false && \
    rm gcloud.tar.gz

# Set PATH for gcloud
ENV PATH="/google-cloud-sdk/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Railway uses PORT environment variable
EXPOSE $PORT

# Start command
CMD gunicorn main:app --bind 0.0.0.0:$PORT
