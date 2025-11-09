from flask import Flask, jsonify
import subprocess
import os
import threading
import time

app = Flask(__name__)

# Global status for installation
install_status = {"running": False, "completed": False, "error": None}

@app.route('/')
def hello():
    return "Google CLI setup ready - use /install to start installation"

@app.route('/status')
def status():
    """Check installation status"""
    gcloud_path = "/opt/render/project/src/google-cloud-sdk/bin/gcloud"
    return {
        "gcloud_exists": os.path.exists(gcloud_path),
        "install_running": install_status["running"],
        "install_completed": install_status["completed"],
        "install_error": install_status["error"]
    }

def install_gcloud_background():
    """Background installation to avoid worker timeout"""
    global install_status
    try:
        install_status["running"] = True
        
        # Quick installation
        result = subprocess.run([
            "bash", "-c", 
            "cd /opt/render/project/src && "
            "curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-455.0.0-linux-x86_64.tar.gz && "
            "tar -xf google-cloud-cli-455.0.0-linux-x86_64.tar.gz && "
            "rm google-cloud-cli-455.0.0-linux-x86_64.tar.gz"
        ], timeout=120, capture_output=True, text=True)
        
        if result.returncode == 0:
            install_status["completed"] = True
        else:
            install_status["error"] = result.stderr
            
    except Exception as e:
        install_status["error"] = str(e)
    finally:
        install_status["running"] = False

@app.route('/install')
def install():
    """Start background installation"""
    if install_status["running"]:
        return {"message": "Installation already running - check /status"}
    
    if install_status["completed"]:
        return {"message": "Already installed - use /test"}
    
    # Start background installation
    thread = threading.Thread(target=install_gcloud_background)
    thread.daemon = True
    thread.start()
    
    return {"message": "Installation started in background - check /status"}

@app.route('/test')
def test():
    """Quick test of gcloud"""
    gcloud_path = "/opt/render/project/src/google-cloud-sdk/bin/gcloud"
    
    if not os.path.exists(gcloud_path):
        return {"error": "gcloud not found - run /install first"}
    
    return {
        "gcloud_exists": True,
        "gcloud_executable": os.access(gcloud_path, os.X_OK),
        "message": "gcloud is ready to use"
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
