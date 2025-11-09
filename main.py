from flask import Flask, jsonify
import subprocess
import os

app = Flask(__name__)

# Correct gcloud path for Render
GCLOUD_PATH = "/opt/render/project/src/google-cloud-sdk/bin/gcloud"

@app.route('/')
def hello():
    return "Google CLI installed and ready!"

@app.route('/gcloud/version')
def gcloud_version():
    try:
        result = subprocess.run([GCLOUD_PATH, 'version'], capture_output=True, text=True, timeout=10)
        return {"output": result.stdout, "error": result.stderr, "path": GCLOUD_PATH}
    except Exception as e:
        return {"error": str(e), "path": GCLOUD_PATH}

@app.route('/gcloud/info')
def gcloud_info():
    try:
        result = subprocess.run([GCLOUD_PATH, 'info'], capture_output=True, text=True, timeout=10)
        return {"output": result.stdout, "error": result.stderr}
    except Exception as e:
        return {"error": str(e)}

@app.route('/check')
def check_installation():
    return {
        "gcloud_exists": os.path.exists(GCLOUD_PATH),
        "gcloud_path": GCLOUD_PATH,
        "is_executable": os.access(GCLOUD_PATH, os.X_OK) if os.path.exists(GCLOUD_PATH) else False
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
