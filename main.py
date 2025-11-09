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
        # Set environment variables for gcloud with Python 3.10
        env = os.environ.copy()
        env['CLOUDSDK_CORE_DISABLE_PROMPTS'] = '1'
        env['CLOUDSDK_PYTHON'] = '/usr/bin/python3.10'  # Use system Python 3.10
        
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

@app.route('/python/check')
def check_python():
    try:
        # Check available Python versions
        result = subprocess.run(['which', 'python3.10'], capture_output=True, text=True)
        python310_path = result.stdout.strip()
        
        result2 = subprocess.run(['python3', '--version'], capture_output=True, text=True)
        current_version = result2.stdout.strip()
        
        return {
            "current_python": current_version,
            "python3.10_path": python310_path if python310_path else "Not found",
            "available_pythons": os.listdir('/usr/bin/') if os.path.exists('/usr/bin/') else []
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
