FROM ubuntu:20.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Google Cloud CLI
RUN curl https://sdk.cloud.google.com | bash
ENV PATH="/root/google-cloud-sdk/bin:${PATH}"

# Copy your application files
COPY . /app
WORKDIR /app

# Install app dependencies (if you have requirements.txt)
# RUN pip3 install -r requirements.txt

# Expose port (adjust as needed)
EXPOSE 8080

# Start command (adjust as needed)
CMD ["python3", "app.py"]
