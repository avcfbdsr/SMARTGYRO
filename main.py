from flask import Flask, jsonify
import subprocess
import os
import json

app = Flask(__name__)

@app.route('/debug/env')
def debug_env():
    """Debug environment variables"""
    env_var = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
    return {
        "env_var_exists": bool(env_var),
        "env_var_length": len(env_var) if env_var else 0,
        "env_var_starts_with": env_var[:50] if env_var else None,
        "all_env_vars": list(os.environ.keys())
    }

@app.route('/auth/setup')
def setup_auth():
    """Setup and activate service account authentication"""
    try:
        service_account_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
        if not service_account_json:
            return {"success": False, "error": "GOOGLE_SERVICE_ACCOUNT_JSON environment variable not set"}
        
        # Try to parse JSON
        try:
            json.loads(service_account_json)
        except json.JSONDecodeError as e:
            return {"success": False, "error": f"Invalid JSON in environment variable: {str(e)}"}
        
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

@app.route('/')
def hello():
    return "Google CLI on Railway - Ready to use!"

@app.route('/health')
def health():
    return {
        "status": "healthy",
        "platform": "Railway",
        "gcloud": "installed",
        "service_account_env": bool(os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON'))
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
