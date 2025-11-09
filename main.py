from flask import Flask, jsonify
import subprocess
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return "Google CLI on Railway - Ready to use!"

@app.route('/gcloud/version')
def gcloud_version():
    try:
        result = subprocess.run(['gcloud', 'version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=10)
        return {
            "success": True,
            "output": result.stdout,
            "error": result.stderr
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/gcloud/auth/list')
def auth_list():
    try:
        result = subprocess.run(['gcloud', 'auth', 'list'], 
                              capture_output=True, 
                              text=True, 
                              timeout=10)
        return {
            "success": True,
            "output": result.stdout,
            "error": result.stderr
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/gcloud/config/list')
def config_list():
    try:
        result = subprocess.run(['gcloud', 'config', 'list'], 
                              capture_output=True, 
                              text=True, 
                              timeout=10)
        return {
            "success": True,
            "output": result.stdout,
            "error": result.stderr
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/health')
def health():
    return {
        "status": "healthy",
        "platform": "Railway",
        "gcloud": "installed"
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
