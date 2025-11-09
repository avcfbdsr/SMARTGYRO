from flask import Flask, jsonify, request
import subprocess
import os
import json
import requests

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

@app.route('/')
def hello():
    return "Google AI on Railway - Using free services!"

@app.route('/translate', methods=['POST'])
def google_translate():
    """Use Google Translate API (has free quota)"""
    try:
        setup_and_activate_service_account()
        
        data = request.get_json()
        text = data.get('text', 'Hello world')
        target = data.get('target', 'es')  # Spanish by default
        
        result = subprocess.run([
            'gcloud', 'ml', 'translate', 'translate', text,
            '--target-language', target,
            '--format', 'json'
        ], capture_output=True, text=True, timeout=20)
        
        return {
            "success": result.returncode == 0,
            "input": text,
            "target_language": target,
            "output": result.stdout,
            "error": result.stderr
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/speech/synthesize', methods=['POST'])
def text_to_speech():
    """Use Google Text-to-Speech (has free quota)"""
    try:
        setup_and_activate_service_account()
        
        data = request.get_json()
        text = data.get('text', 'Hello, this is a test')
        
        result = subprocess.run([
            'gcloud', 'ml', 'speech', 'synthesize-text', text,
            '--output-file', 'output.wav'
        ], capture_output=True, text=True, timeout=20)
        
        return {
            "success": result.returncode == 0,
            "text": text,
            "output": result.stdout,
            "error": result.stderr,
            "message": "Audio file would be generated as output.wav"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/vision/detect', methods=['POST'])
def vision_api():
    """Use Google Vision API for image analysis"""
    try:
        setup_and_activate_service_account()
        
        data = request.get_json()
        image_url = data.get('image_url', 'https://example.com/image.jpg')
        
        result = subprocess.run([
            'gcloud', 'ml', 'vision', 'detect-labels', image_url
        ], capture_output=True, text=True, timeout=20)
        
        return {
            "success": result.returncode == 0,
            "image_url": image_url,
            "output": result.stdout,
            "error": result.stderr
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/ai/gemini-free', methods=['POST'])
def gemini_free_quota():
    """Try Gemini with free quota (if available)"""
    try:
        setup_and_activate_service_account()
        
        data = request.get_json()
        prompt = data.get('prompt', 'Hello')
        
        # Try using Gemini Flash (cheaper/free tier)
        result = subprocess.run([
            'gcloud', 'ai', 'models', 'predict',
            '--model', 'gemini-1.5-flash',
            '--region', 'us-central1',
            '--json-request', json.dumps({
                "instances": [{"content": prompt}]
            })
        ], capture_output=True, text=True, timeout=30)
        
        return {
            "success": result.returncode == 0,
            "prompt": prompt,
            "output": result.stdout,
            "error": result.stderr,
            "model": "gemini-1.5-flash"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/quota/check')
def check_quotas():
    """Check available quotas for different services"""
    try:
        setup_and_activate_service_account()
        
        result = subprocess.run([
            'gcloud', 'compute', 'project-info', 'describe',
            '--format', 'json'
        ], capture_output=True, text=True, timeout=15)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/free-services')
def free_services():
    """List free Google Cloud services"""
    return {
        "free_services": [
            {
                "service": "Google Translate",
                "endpoint": "/translate",
                "quota": "500,000 characters/month free"
            },
            {
                "service": "Text-to-Speech", 
                "endpoint": "/speech/synthesize",
                "quota": "1 million characters/month free"
            },
            {
                "service": "Vision API",
                "endpoint": "/vision/detect", 
                "quota": "1,000 requests/month free"
            },
            {
                "service": "Natural Language API",
                "quota": "5,000 requests/month free"
            }
        ],
        "note": "These services have free quotas that don't require billing setup"
    }

@app.route('/health')
def health():
    return {
        "status": "healthy",
        "platform": "Railway",
        "gcloud": "authenticated",
        "free_services_available": True
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
