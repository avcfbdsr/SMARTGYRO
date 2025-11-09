#!/bin/bash
# Install Google Cloud CLI on Render

# Download and install gcloud
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Add to PATH
echo 'source ~/google-cloud-sdk/path.bash.inc' >> ~/.bashrc
echo 'source ~/google-cloud-sdk/completion.bash.inc' >> ~/.bashrc

# Reload shell
source ~/.bashrc

# Verify installation
gcloud version
