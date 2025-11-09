from flask import Flask, jsonify, request, redirect
import subprocess
import os
import json
import re

app = Flask(__name__)

@app.route('/')
def hello():
    return "Google Personal Auth - Get free Gemini access!"

@app.route('/auth/get-link')
def get_auth_link():
    """Get Google OAuth link for personal account login"""
    try:
        # Run gcloud auth login with no-launch-browser to get the link
        result = subprocess.run([
            'gcloud', 'auth', 'login', '--no-launch-browser'
        ], capture_output=True, text=True, timeout=30, input='\n')
        
        # Extract the OAuth URL from the output
        output = result.stderr + result.stdout
        
        # Look for the OAuth URL
        url_pattern = r'https://accounts\.google\.com/o/oauth2/auth[^\s]+'
        urls = re.findall(url_pattern, output)
        
        if urls:
            auth_url = urls[0]
            return {
                "success": True,
                "auth_url": auth_url,
                "instructions": [
                    "1. Click the auth_url above",
                    "2. Login with your personal Google account", 
                    "3. Copy the verification code",
                    "4. Use POST /auth/verify with the code"
                ],
                "next_step": "POST /auth/verify"
            }
        else:
            return {
                "success": False,
                "error": "Could not extract auth URL",
                "output": output
            }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/auth/verify', methods=['POST'])
def verify_auth():
    """Verify the auth code from Google"""
    try:
        data = request.get_json()
        auth_code = data.get('code', '')
        
        if not auth_code:
            return {"success": False, "error": "Please provide 'code' in JSON body"}
        
        # Complete the authentication with the code
        result = subprocess.run([
            'gcloud', 'auth', 'login', '--no-launch-browser'
        ], capture_output=True, text=True, timeout=30, input=f'{auth_code}\n')
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
            "message": "Authentication completed!" if result.returncode == 0 else "Authentication failed"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/auth/status')
def auth_status():
    """Check current authentication status"""
    try:
        result = subprocess.run([
            'gcloud', 'auth', 'list'
        ], capture_output=True, text=True, timeout=10)
        
        return {
            "success": True,
            "output": result.stdout,
            "error": result.stderr
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/gemini/test', methods=['POST'])
def test_gemini():
    """Test Gemini with personal account (should work without billing)"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', 'Hello, write a Python function to add two numbers')
        
        # Try Gemini API call
        result = subprocess.run([
            'gcloud', 'ai', 'models', 'predict',
            '--model', 'gemini-pro',
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
            "model": "gemini-pro"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/gemini/simple', methods=['GET'])
def simple_gemini():
    """Simple Gemini test with GET request"""
    try:
        prompt = request.args.get('prompt', 'Write a hello world program in Python')
        
        # Use curl to call Vertex AI API directly
        result = subprocess.run([
            'curl', '-X', 'POST',
            f'https://us-central1-aiplatform.googleapis.com/v1/projects/{os.environ.get("GOOGLE_CLOUD_PROJECT", "peppy-bond-477619-a8")}/locations/us-central1/publishers/google/models/gemini-pro:generateContent',
            '-H', 'Authorization: Bearer $(gcloud auth print-access-token)',
            '-H', 'Content-Type: application/json',
            '-d', json.dumps({
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            })
        ], capture_output=True, text=True, timeout=30, shell=True)
        
        return {
            "success": result.returncode == 0,
            "prompt": prompt,
            "output": result.stdout,
            "error": result.stderr
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/instructions')
def instructions():
    """Step-by-step instructions"""
    return {
        "title": "How to get free Gemini access with personal Google account",
        "steps": [
            {
                "step": 1,
                "action": "GET /auth/get-link",
                "description": "Get Google OAuth URL"
            },
            {
                "step": 2, 
                "action": "Click the auth_url in your browser",
                "description": "Login with your personal Google account"
            },
            {
                "step": 3,
                "action": "Copy the verification code from browser",
                "description": "Google will show you a code"
            },
            {
                "step": 4,
                "action": "POST /auth/verify with {\"code\": \"your-code\"}",
                "description": "Complete authentication"
            },
            {
                "step": 5,
                "action": "POST /gemini/test with {\"prompt\": \"your question\"}",
                "description": "Use Gemini for free!"
            }
        ],
        "note": "Personal Google accounts get free quotas without billing setup"
    }

@app.route('/health')
def health():
    return {
        "status": "healthy",
        "platform": "Railway",
        "auth_method": "Personal Google Account (Free)",
        "gemini_available": "After personal auth"
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
