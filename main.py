from flask import Flask, jsonify
import subprocess
import os
import json

app = Flask(__name__)

def setup_service_account():
    """Create service account file from environment variable"""
    try:
        service_account_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
        if service_account_json:
            with open('service-account.json', 'w') as f:
                f.write(service_account_json)
            return True
    except:
        pass
    return False

@app.route('/')
def hello():
    return "Google CLI on Railway - Authenticated and Ready!"

@app.route('/auth/setup')
def setup_auth():
    """Setup and activate service account authentication"""
    try:
        service_account_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
        if not service_account_json:
            return {"success": False, "error": "GOOGLE_SERVICE_ACCOUNT_JSON environment variable not set"}
        
        # Create service account file
        with open('service-account.json', 'w') as f:
            f.write(service_account_json)
        
        # Authenticate
        result = subprocess.run([
            'gcloud', 'auth', 'activate-service-account', 
            '--key-file=service-account.json'
        ], capture_output=True, text=True, timeout=15)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

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

@app.route('/gcloud/projects')
def list_projects():
    """List Google Cloud projects (requires authentication)"""
    try:
        # Auto-setup service account if not already done
        setup_service_account()
        
        result = subprocess.run(['gcloud', 'projects', 'list'], 
                              capture_output=True, 
                              text=True, 
                              timeout=15)
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
        "gcloud": "installed",
        "authenticated": True,
        "service_account": "railway-app@peppy-bond-477619-a8.iam.gserviceaccount.com"
    }

# Auto-authenticate on startup
with app.app_context():
    setup_service_account()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
