from flask import Flask, jsonify
import subprocess
import os
import json

app = Flask(__name__)

def setup_and_activate_service_account():
    """Setup service account and set as active account"""
    try:
        service_account_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
        if not service_account_json:
            return False, "No service account JSON found"
        
        # Create service account file
        with open('service-account.json', 'w') as f:
            f.write(service_account_json)
        
        # Activate service account
        result1 = subprocess.run([
            'gcloud', 'auth', 'activate-service-account', 
            '--key-file=service-account.json'
        ], capture_output=True, text=True, timeout=15)
        
        if result1.returncode != 0:
            return False, f"Activation failed: {result1.stderr}"
        
        # Set as active account
        result2 = subprocess.run([
            'gcloud', 'config', 'set', 'account', 
            'railway-app@peppy-bond-477619-a8.iam.gserviceaccount.com'
        ], capture_output=True, text=True, timeout=10)
        
        if result2.returncode != 0:
            return False, f"Set account failed: {result2.stderr}"
        
        return True, "Service account activated and set as active"
        
    except Exception as e:
        return False, str(e)

@app.route('/')
def hello():
    return "Google CLI on Railway - Authenticated and Ready!"

@app.route('/auth/setup')
def setup_auth():
    """Setup and activate service account authentication"""
    success, message = setup_and_activate_service_account()
    return {
        "success": success,
        "message": message
    }

@app.route('/gcloud/projects')
def list_projects():
    """List Google Cloud projects (requires authentication)"""
    try:
        # Ensure authentication is set up
        setup_and_activate_service_account()
        
        result = subprocess.run(['gcloud', 'projects', 'list'], 
                              capture_output=True, 
                              text=True, 
                              timeout=15)
        return {
            "success": result.returncode == 0,
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
        "gcloud": "installed",
        "service_account": "railway-app@peppy-bond-477619-a8.iam.gserviceaccount.com"
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
