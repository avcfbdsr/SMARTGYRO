from flask import Flask, jsonify
import subprocess
import os
from gcloud_auth import setup_gcloud_auth

# Setup Google Cloud authentication
setup_gcloud_auth()

app = Flask(__name__)

# Set gcloud path
GCLOUD_PATH = "/opt/render/project/src/google-cloud-sdk/bin/gcloud"

@app.route('/')
def hello():
    return "Google CLI installed and ready!"

@app.route('/gcloud/version')
def gcloud_version():
    try:
        result = subprocess.run([GCLOUD_PATH, 'version'], capture_output=True, text=True)
        return {"output": result.stdout, "error": result.stderr}
    except Exception as e:
        return {"error": str(e)}

@app.route('/gcloud/which')
def which_gcloud():
    try:
        result = subprocess.run(['which', 'gcloud'], capture_output=True, text=True)
        return {"output": result.stdout, "error": result.stderr}
    except Exception as e:
        return {"error": str(e)}

@app.route('/gcloud/path')
def check_path():
    return {"PATH": os.environ.get('PATH', 'Not found')}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
