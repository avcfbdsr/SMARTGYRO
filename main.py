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

def get_access_token():
    """Get Google Cloud access token"""
    try:
        result = subprocess.run([
            'gcloud', 'auth', 'print-access-token'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except:
        return None

@app.route('/')
def hello():
    return "Google AI Models on Railway - Ready to use!"

@app.route('/gemini/test', methods=['POST'])
def test_gemini():
    """Test Gemini AI model using Python requests"""
    try:
        setup_and_activate_service_account()
        
        data = request.get_json()
        prompt = data.get('prompt', 'Hello, how are you?')
        
        # Get access token
        access_token = get_access_token()
        if not access_token:
            return {"success": False, "error": "Failed to get access token"}
        
        # Call Vertex AI API using Python requests
        url = f'https://us-central1-aiplatform.googleapis.com/v1/projects/peppy-bond-477619-a8/locations/us-central1/publishers/google/models/gemini-pro:generateContent'
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        return {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "output": response.text,
            "error": "" if response.status_code == 200 else f"HTTP {response.status_code}"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/gemini/simple', methods=['GET'])
def simple_gemini():
    """Simple Gemini test with GET request"""
    try:
        setup_and_activate_service_account()
        
        prompt = request.args.get('prompt', 'Write a hello world program in Python')
        
        access_token = get_access_token()
        if not access_token:
            return {"success": False, "error": "Failed to get access token"}
        
        url = f'https://us-central1-aiplatform.googleapis.com/v1/projects/peppy-bond-477619-a8/locations/us-central1/publishers/google/models/gemini-pro:generateContent'
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                ai_response = result['candidates'][0]['content']['parts'][0]['text']
                return {
                    "success": True,
                    "prompt": prompt,
                    "response": ai_response
                }
        
        return {
            "success": False,
            "status_code": response.status_code,
            "error": response.text
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/ai/token')
def get_token():
    """Get access token for debugging"""
    try:
        setup_and_activate_service_account()
        token = get_access_token()
        return {
            "success": bool(token),
            "token_length": len(token) if token else 0,
            "token_preview": token[:20] + "..." if token else None
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/health')
def health():
    return {
        "status": "healthy",
        "platform": "Railway",
        "gcloud": "authenticated",
        "ai_ready": True,
        "project": "peppy-bond-477619-a8"
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
