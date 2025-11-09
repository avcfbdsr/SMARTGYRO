from flask import Flask, jsonify, request
import subprocess
import os
import json
import re
import threading
import time

app = Flask(__name__)

# Global variable to store auth process
auth_process = None
auth_output = ""

@app.route('/')
def hello():
    return "Google Personal Auth - Fixed OAuth Flow!"

@app.route('/auth/start')
def start_auth():
    """Start the authentication process and capture output"""
    global auth_process, auth_output
    
    try:
        # Reset any existing authentication
        subprocess.run(['gcloud', 'auth', 'revoke', '--all'], 
                      capture_output=True, text=True, timeout=10)
        
        # Start auth process in background
        auth_process = subprocess.Popen([
            'gcloud', 'auth', 'login', 
            '--no-launch-browser',
            '--enable-gdrive-access'
        ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, 
           stderr=subprocess.PIPE, text=True)
        
        # Give it a moment to generate the URL
        time.sleep(2)
        
        # Read the output
        try:
            stdout, stderr = auth_process.communicate(timeout=5)
            auth_output = stdout + stderr
        except subprocess.TimeoutExpired:
            # Process is still running, read what we can
            auth_output = "Process started, check /auth/get-url for the link"
        
        return {
            "success": True,
            "message": "Authentication process started",
            "next_step": "GET /auth/get-url to get the login link"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/auth/get-url')
def get_auth_url():
    """Get the authentication URL from the running process"""
    global auth_output
    
    try:
        # Try to get fresh output
        result = subprocess.run([
            'gcloud', 'auth', 'login', '--no-launch-browser', '--brief'
        ], capture_output=True, text=True, timeout=10, input='\n')
        
        output = result.stdout + result.stderr
        
        # Look for the Google OAuth URL
        url_patterns = [
            r'https://accounts\.google\.com/o/oauth2/auth[^\s\n]+',
            r'https://accounts\.google\.com/oauth/authorize[^\s\n]+',
            r'Please visit this URL to authorize this application: (https://[^\s\n]+)'
        ]
        
        auth_url = None
        for pattern in url_patterns:
            matches = re.findall(pattern, output)
            if matches:
                auth_url = matches[0]
                if isinstance(auth_url, tuple):
                    auth_url = auth_url[0]
                break
        
        if auth_url:
            return {
                "success": True,
                "auth_url": auth_url,
                "instructions": [
                    "1. Copy the auth_url above",
                    "2. Open it in your browser",
                    "3. Login with your personal Google account",
                    "4. Copy the authorization code",
                    "5. Use POST /auth/complete with the code"
                ]
            }
        else:
            return {
                "success": False,
                "error": "Could not find auth URL in output",
                "output": output,
                "suggestion": "Try /auth/manual for manual steps"
            }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/auth/complete', methods=['POST'])
def complete_auth():
    """Complete authentication with the code from browser"""
    try:
        data = request.get_json()
        auth_code = data.get('code', '').strip()
        
        if not auth_code:
            return {"success": False, "error": "Please provide 'code' in request body"}
        
        # Complete the authentication
        result = subprocess.run([
            'gcloud', 'auth', 'login', '--no-launch-browser'
        ], input=f'{auth_code}\n', capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            # Set the project
            subprocess.run([
                'gcloud', 'config', 'set', 'project', 'peppy-bond-477619-a8'
            ], capture_output=True, text=True, timeout=10)
            
            return {
                "success": True,
                "message": "Authentication successful!",
                "output": result.stdout,
                "next_step": "Now you can use /gemini/test for free Gemini access"
            }
        else:
            return {
                "success": False,
                "error": result.stderr,
                "output": result.stdout
            }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/auth/manual')
def manual_auth():
    """Manual authentication instructions"""
    return {
        "title": "Manual Authentication Steps",
        "method": "Use your browser to complete authentication",
        "steps": [
            {
                "step": 1,
                "description": "Open this URL in your browser:",
                "url": "https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=764086051850-6qr4p6gpi6hn506pt8ejuq83di341hur.apps.googleusercontent.com&redirect_uri=urn%3Aietf%3Awg%3Aoauth%3A2.0%3Aoob&scope=https%3A//www.googleapis.com/auth/userinfo.email%20https%3A//www.googleapis.com/auth/cloud-platform%20https%3A//www.googleapis.com/auth/appengine.admin%20https%3A//www.googleapis.com/auth/compute%20https%3A//www.googleapis.com/auth/accounts.reauth&code_challenge_method=S256&code_challenge=PLACEHOLDER"
            },
            {
                "step": 2,
                "description": "Login with your personal Google account"
            },
            {
                "step": 3,
                "description": "Copy the authorization code from the browser"
            },
            {
                "step": 4,
                "description": "Send POST request to /auth/complete with the code"
            }
        ],
        "note": "This gives you free access to Google AI services"
    }

@app.route('/auth/status')
def auth_status():
    """Check authentication status"""
    try:
        result = subprocess.run([
            'gcloud', 'auth', 'list'
        ], capture_output=True, text=True, timeout=10)
        
        return {
            "success": True,
            "authenticated": "ACTIVE" in result.stdout,
            "output": result.stdout,
            "error": result.stderr
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/gemini/test', methods=['POST'])
def test_gemini():
    """Test Gemini with personal account"""
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
                "error": "Not authenticated. Use /auth/start first.",
                "auth_required": True
            }
        
        access_token = token_result.stdout.strip()
        
        # Call Gemini API
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
            "status_code": response.status_code,
            "model": "gemini-pro"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/health')
def health():
    return {
        "status": "healthy",
        "platform": "Railway",
        "auth_method": "Personal Google Account",
        "gemini_access": "Free with personal auth"
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
