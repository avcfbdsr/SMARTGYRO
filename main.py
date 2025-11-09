from flask import Flask, jsonify, request
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
        
        with open('service-account.json', 'w') as f:
            f.write(service_account_json)
        
        subprocess.run([
            'gcloud', 'auth', 'activate-service-account', 
            '--key-file=service-account.json'
        ], capture_output=True, text=True, timeout=15)
        
        subprocess.run([
            'gcloud', 'config', 'set', 'account', 
            'railway-app@peppy-bond-477619-a8.iam.gserviceaccount.com'
        ], capture_output=True, text=True, timeout=10)
        
        subprocess.run([
            'gcloud', 'config', 'set', 'project', 'peppy-bond-477619-a8'
        ], capture_output=True, text=True, timeout=10)
        
        return True, "Service account activated"
        
    except Exception as e:
        return False, str(e)

def install_beta_components():
    """Install beta components quietly"""
    try:
        result = subprocess.run([
            'gcloud', 'components', 'install', 'beta', '--quiet'
        ], capture_output=True, text=True, timeout=60)
        return result.returncode == 0
    except:
        return False

def enable_api(api_name):
    """Enable API quietly"""
    try:
        result = subprocess.run([
            'gcloud', 'services', 'enable', api_name, '--quiet'
        ], capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stderr
    except Exception as e:
        return False, str(e)

@app.route('/')
def hello():
    return "Google ML APIs on Railway - Auto-enabling APIs!"

@app.route('/setup/install-beta')
def install_beta():
    """Install beta components"""
    try:
        setup_and_activate_service_account()
        success = install_beta_components()
        return {
            "success": success,
            "message": "Beta components installed" if success else "Failed to install beta components"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/setup/enable-apis')
def enable_apis():
    """Enable required APIs"""
    try:
        setup_and_activate_service_account()
        
        apis = [
            'language.googleapis.com',
            'translate.googleapis.com'
        ]
        
        results = []
        for api in apis:
            success, error = enable_api(api)
            results.append({
                "api": api,
                "success": success,
                "error": error if not success else "Enabled successfully"
            })
        
        return {"results": results}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/translate', methods=['POST'])
def google_translate():
    """Use Google Translate API with auto-setup"""
    try:
        setup_and_activate_service_account()
        install_beta_components()
        enable_api('translate.googleapis.com')
        
        data = request.get_json()
        text = data.get('text', 'Hello world')
        target = data.get('target', 'es')
        
        result = subprocess.run([
            'gcloud', 'beta', 'ml', 'translate', 'translate-text',
            '--content', text,
            '--target-language', target,
            '--format', 'json',
            '--quiet'
        ], capture_output=True, text=True, timeout=30)
        
        return {
            "success": result.returncode == 0,
            "input": text,
            "target_language": target,
            "output": result.stdout,
            "error": result.stderr
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/language/sentiment', methods=['POST'])
def analyze_sentiment():
    """Analyze sentiment with auto-setup"""
    try:
        setup_and_activate_service_account()
        enable_api('language.googleapis.com')
        
        data = request.get_json()
        text = data.get('text', 'I love this product!')
        
        result = subprocess.run([
            'gcloud', 'ml', 'language', 'analyze-sentiment',
            '--content', text,
            '--format', 'json',
            '--quiet'
        ], capture_output=True, text=True, timeout=30)
        
        return {
            "success": result.returncode == 0,
            "input": text,
            "output": result.stdout,
            "error": result.stderr
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/simple-test')
def simple_test():
    """Simple test without complex APIs"""
    try:
        setup_and_activate_service_account()
        
        # Test basic gcloud info
        result = subprocess.run([
            'gcloud', 'info', '--format', 'json'
        ], capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            return {
                "success": True,
                "message": "Google Cloud CLI is working!",
                "account": "railway-app@peppy-bond-477619-a8.iam.gserviceaccount.com",
                "project": "peppy-bond-477619-a8"
            }
        else:
            return {
                "success": False,
                "error": result.stderr
            }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/status')
def status():
    """Check current status"""
    return {
        "message": "Google ML APIs require manual API enabling",
        "steps": [
            "1. Go to Google Cloud Console",
            "2. Enable Natural Language API: https://console.developers.google.com/apis/api/language.googleapis.com/overview?project=peppy-bond-477619-a8",
            "3. Enable Translate API: https://console.developers.google.com/apis/api/translate.googleapis.com/overview?project=peppy-bond-477619-a8",
            "4. Wait a few minutes for activation"
        ],
        "working_endpoint": "/simple-test - Basic gcloud test"
    }

@app.route('/health')
def health():
    return {
        "status": "healthy",
        "platform": "Railway",
        "gcloud": "authenticated",
        "note": "APIs need manual enabling in Google Cloud Console"
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
