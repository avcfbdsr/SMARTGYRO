FROM ubuntu:20.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Google Cloud CLI
RUN curl https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-455.0.0-linux-x86_64.tar.gz -o gcloud.tar.gz && \
    tar -xf gcloud.tar.gz && \
    ./google-cloud-sdk/install.sh --quiet --path-update=false && \
    rm gcloud.tar.gz

# Set PATH
ENV PATH="/google-cloud-sdk/bin:${PATH}"

# Copy application files
COPY . /app
WORKDIR /app

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Expose port
EXPOSE 10000

# Start command
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:10000"]
