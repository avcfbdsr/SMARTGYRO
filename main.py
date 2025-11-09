from flask import Flask, jsonify
import subprocess
import os
from gcloud_auth import setup_gcloud_auth

# Setup Google Cloud authentication
setup_gcloud_auth()

app = Flask(__name__)

@app.route('/')
def hello():
    return "Google CLI installed and ready!"

@app.route('/gcloud/version')
def gcloud_version():
    try:
        result = subprocess.run(['gcloud', 'version'], capture_output=True, text=True)
        return {"output": result.stdout, "error": result.stderr}
    except Exception as e:
        return {"error": str(e)}

@app.route('/gcloud/projects')
def list_projects():
    try:
        result = subprocess.run(['gcloud', 'projects', 'list', '--format=json'], capture_output=True, text=True)
        return {"output": result.stdout, "error": result.stderr}
    except Exception as e:
        return {"error": str(e)}

@app.route('/gcloud/config')
def show_config():
    try:
        result = subprocess.run(['gcloud', 'config', 'list'], capture_output=True, text=True)
        return {"output": result.stdout, "error": result.stderr}
    except Exception as e:
        return {"error": str(e)}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
