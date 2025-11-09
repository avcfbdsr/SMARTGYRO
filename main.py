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
        # Set environment variables for gcloud
        env = os.environ.copy()
        env['CLOUDSDK_CORE_DISABLE_PROMPTS'] = '1'
        env['CLOUDSDK_PYTHON'] = 'python3'
        
        result = subprocess.run([GCLOUD_PATH, 'version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=30,
                              env=env)
        return {"output": result.stdout, "error": result.stderr, "returncode": result.returncode}
    except subprocess.TimeoutExpired:
        return {"error": "Command timed out after 30 seconds"}
    except Exception as e:
        return {"error": str(e)}

@app.route('/gcloud/quick')
def gcloud_quick():
    try:
        # Quick test with shorter timeout
        env = os.environ.copy()
        env['CLOUDSDK_CORE_DISABLE_PROMPTS'] = '1'
        
        result = subprocess.run([GCLOUD_PATH, '--help'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5,
                              env=env)
        return {"output": result.stdout[:500], "error": result.stderr, "returncode": result.returncode}
    except subprocess.TimeoutExpired:
        return {"error": "Quick test timed out"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
