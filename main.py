from flask import Flask, jsonify, request
import subprocess
import os
import json

app = Flask(__name__)

@app.route('/')
def hello():
    return "Simple Google Auth - Bypass OAuth issues!"

@app.route('/auth/direct', methods=['POST'])
def direct_auth():
    """Direct authentication with verification code"""
    try:
        data = request.get_json()
        verification_code = data.get('code', '').strip()
        
        if not verification_code:
            return {
                "success": False,
                "error": "Please provide verification code",
                "instructions": [
                    "1. Run: gcloud auth login --no-launch-browser (on your local machine)",
                    "2. Copy the verification code from browser",
                    "3. Send it here with POST /auth/direct {\"code\": \"your-code\"}"
                ]
            }
        
        # Try to authenticate directly with the code
        # First, revoke existing auth
        subprocess.run(['gcloud', 'auth', 'revoke', '--all'], 
                      capture_output=True, text=True)
        
        # Use a different approach - create credentials file
        result = subprocess.run([
            'gcloud', 'auth', 'login', '--cred-file=/dev/stdin'
        ], input=verification_code, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return {
                "success": True,
                "message": "Authentication successful!",
                "output": result.stdout
            }
        else:
            # Try alternative method
            result2 = subprocess.run([
                'bash', '-c', f'echo "{verification_code}" | gcloud auth login --no-launch-browser'
            ], capture_output=True, text=True, timeout=30)
            
            return {
                "success": result2.returncode == 0,
                "message": "Authentication completed" if result2.returncode == 0 else "Authentication failed",
                "output": result2.stdout,
                "error": result2.stderr
            }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/auth/manual-steps')
def manual_steps():
    """Manual steps to get authenticated"""
    return {
        "title": "Manual Authentication (Bypass OAuth issues)",
        "steps": [
            {
                "step": 1,
                "description": "On your LOCAL computer, run:",
                "command": "gcloud auth login --no-launch-browser"
            },
            {
                "step": 2,
                "description": "Copy the verification code from the browser"
            },
            {
                "step": 3,
                "description": "Send the code to this endpoint:",
                "endpoint": "POST /auth/direct",
                "body": {"code": "your-verification-code"}
            }
        ],
        "example_code": """
import requests
response = requests.post("https://smartgyro-production.up.railway.app/auth/direct",
                        json={"code": "4/0Ab32j914gml0MsTtOUsfsDa_2rnyxLbHurqrY5-BA3lNFZDhUL8LZC59bCI1knLIAMY57g"})
print(response.json())
        """,
        "note": "Use the verification code from your browser"
    }

@app.route('/auth/alternative')
def auth_alternative():
    """Alternative authentication method"""
    return {
        "message": "Since OAuth has issues, let's try a different approach",
        "alternative_methods": [
            {
                "method": "Application Default Credentials",
                "description": "Use your local gcloud credentials",
                "steps": [
                    "1. On your local machine: gcloud auth application-default login",
                    "2. Copy the credentials file to Railway",
                    "3. Set GOOGLE_APPLICATION_CREDENTIALS environment variable"
                ]
            },
            {
                "method": "Service Account with User Access",
                "description": "Create a service account with your personal project",
                "steps": [
                    "1. Create a new Google Cloud project with your personal account",
                    "2. Create a service account in that project", 
                    "3. Download the JSON key",
                    "4. Use it in Railway"
                ]
            }
        ]
    }

@app.route('/test-current-auth')
def test_current_auth():
    """Test if any authentication is working"""
    try:
        # Test gcloud auth list
        result1 = subprocess.run(['gcloud', 'auth', 'list'], 
                                capture_output=True, text=True, timeout=10)
        
        # Test access token
        result2 = subprocess.run(['gcloud', 'auth', 'print-access-token'], 
                                capture_output=True, text=True, timeout=10)
        
        # Test project info
        result3 = subprocess.run(['gcloud', 'config', 'list'], 
                                capture_output=True, text=True, timeout=10)
        
        return {
            "auth_list": {
                "success": result1.returncode == 0,
                "output": result1.stdout,
                "error": result1.stderr
            },
            "access_token": {
                "success": result2.returncode == 0,
                "has_token": len(result2.stdout.strip()) > 0,
                "error": result2.stderr
            },
            "config": {
                "success": result3.returncode == 0,
                "output": result3.stdout,
                "error": result3.stderr
            }
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/gemini/test', methods=['POST'])
def test_gemini():
    """Test Gemini (will work once authenticated)"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', 'Write a Python hello world program')
        
        # Get access token
        token_result = subprocess.run([
            'gcloud', 'auth', 'print-access-token'
        ], capture_output=True, text=True, timeout=10)
        
        if token_result.returncode != 0:
            return {
                "success": False,
                "error": "Not authenticated. Use /auth/direct first.",
                "auth_required": True
            }
        
        access_token = token_result.stdout.strip()
        
        # Test with a simple API call first
        import requests
        url = 'https://us-central1-aiplatform.googleapis.com/v1/projects/peppy-bond-477619-a8/locations/us-central1/publishers/google/models/gemini-pro:generateContent'
        
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
            "prompt": prompt,
            "response": response.json() if response.status_code == 200 else response.text,
            "status_code": response.status_code
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/health')
def health():
    return {
        "status": "healthy",
        "platform": "Railway",
        "note": "Use /auth/manual-steps for authentication instructions"
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
