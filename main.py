from flask import Flask, jsonify
import subprocess
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return "Google CLI setup ready - use /install to complete installation"

@app.route('/install')
def install_gcloud():
    """Manual gcloud installation endpoint"""
    try:
        # Simple installation without interactive prompts
        commands = [
            "cd /opt/render/project/src",
            "curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-455.0.0-linux-x86_64.tar.gz",
            "tar -xf google-cloud-cli-455.0.0-linux-x86_64.tar.gz",
            "rm google-cloud-cli-455.0.0-linux-x86_64.tar.gz",
            "./google-cloud-sdk/install.sh --quiet --install-python=false --path-update=false"
        ]
        
        result = subprocess.run(" && ".join(commands), 
                              shell=True, 
                              capture_output=True, 
                              text=True, 
                              timeout=60)
        
        return {
            "status": "Installation completed",
            "output": result.stdout,
            "error": result.stderr,
            "returncode": result.returncode
        }
    except Exception as e:
        return {"error": str(e)}

@app.route('/test')
def test_gcloud():
    """Test if gcloud is working"""
    gcloud_path = "/opt/render/project/src/google-cloud-sdk/bin/gcloud"
    
    if not os.path.exists(gcloud_path):
        return {"error": "gcloud not installed - visit /install first"}
    
    try:
        env = os.environ.copy()
        env['CLOUDSDK_CORE_DISABLE_PROMPTS'] = '1'
        env['CLOUDSDK_PYTHON'] = '/usr/bin/python3.11'
        
        result = subprocess.run([gcloud_path, 'version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5,
                              env=env)
        
        return {
            "gcloud_works": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
