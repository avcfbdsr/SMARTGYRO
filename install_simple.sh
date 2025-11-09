#!/bin/bash
# Simple Google CLI installation
curl https://sdk.cloud.google.com | bash
source ~/google-cloud-sdk/path.bash.inc
export PATH="$HOME/google-cloud-sdk/bin:$PATH"
