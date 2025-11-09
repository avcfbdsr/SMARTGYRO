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

@app.route('/')
def hello():
    return "Google AI Models on Railway - Ready to use!"

@app.route('/ai/models')
def list_ai_models():
    """List available AI models"""
    try:
        setup_and_activate_service_account()
        
        result = subprocess.run([
            'gcloud', 'ai', 'models', 'list', '--region=us-central1'
        ], capture_output=True, text=True, timeout=20)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/ai/endpoints')
def list_ai_endpoints():
    """List AI endpoints"""
    try:
        setup_and_activate_service_account()
        
        result = subprocess.run([
            'gcloud', 'ai', 'endpoints', 'list', '--region=us-central1'
        ], capture_output=True, text=True, timeout=20)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/vertex/models')
def vertex_models():
    """List Vertex AI models"""
    try:
        setup_and_activate_service_account()
        
        result = subprocess.run([
            'gcloud', 'ai', 'models', 'list', 
            '--region=us-central1',
            '--format=json'
        ], capture_output=True, text=True, timeout=20)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/gemini/test', methods=['POST'])
def test_gemini():
    """Test Gemini AI model"""
    try:
        setup_and_activate_service_account()
        
        data = request.get_json()
        prompt = data.get('prompt', 'Hello, how are you?')
        
        # Use curl to call Vertex AI API
        result = subprocess.run([
            'curl', '-X', 'POST',
            f'https://us-central1-aiplatform.googleapis.com/v1/projects/peppy-bond-477619-a8/locations/us-central1/publishers/google/models/gemini-pro:generateContent',
            '-H', f'Authorization: Bearer $(gcloud auth print-access-token)',
            '-H', 'Content-Type: application/json',
            '-d', json.dumps({
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            })
        ], capture_output=True, text=True, timeout=30, shell=True)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/ai/enable')
def enable_ai_apis():
    """Enable required AI APIs"""
    try:
        setup_and_activate_service_account()
        
        apis = [
            'aiplatform.googleapis.com',
            'ml.googleapis.com',
            'compute.googleapis.com'
        ]
        
        results = []
        for api in apis:
            result = subprocess.run([
                'gcloud', 'services', 'enable', api
            ], capture_output=True, text=True, timeout=30)
            
            results.append({
                "api": api,
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            })
        
        return {"results": results}
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
