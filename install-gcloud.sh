#!/bin/bash
set -e

# Install dependencies
apt-get update
apt-get install -y curl python3 python3-pip

# Download and install Google Cloud CLI
curl https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-455.0.0-linux-x86_64.tar.gz -o gcloud.tar.gz
tar -xf gcloud.tar.gz
./google-cloud-sdk/install.sh --quiet --path-update=true

# Add to PATH permanently
echo 'export PATH="/opt/render/project/src/google-cloud-sdk/bin:$PATH"' >> ~/.bashrc
export PATH="/opt/render/project/src/google-cloud-sdk/bin:$PATH"

# Verify installation
which gcloud
gcloud version
