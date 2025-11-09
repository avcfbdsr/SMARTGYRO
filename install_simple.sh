#!/bin/bash
set -e

# Download Google Cloud CLI
cd /opt/render/project/src
curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-455.0.0-linux-x86_64.tar.gz
tar -xf google-cloud-cli-455.0.0-linux-x86_64.tar.gz
rm google-cloud-cli-455.0.0-linux-x86_64.tar.gz

# Install quietly
./google-cloud-sdk/install.sh --quiet --path-update=false

# Verify installation
ls -la /opt/render/project/src/google-cloud-sdk/bin/
echo "Google Cloud CLI installed successfully"
