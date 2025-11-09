from flask import Flask, jsonify, request
import subprocess
import os
import json
import requests

app = Flask(__name__)

@app.route('/')
def hello():
    return "Personal Google Cloud Project - Bypass OAuth issues!"

@app.route('/solution')
def solution():
    """The solution to OAuth S256 error"""
    return {
        "problem": "OAuth S256 error is a known gcloud CLI bug on servers",
        "solution": "Create your own Google Cloud project with personal account",
        "steps": [
            {
                "step": 1,
                "title": "Create Personal Google Cloud Project",
                "actions": [
                    "1. Go to https://console.cloud.google.com/",
                    "2. Login with a91308459@gmail.com",
                    "3. Click 'New Project'",
                    "4. Name it 'personal-ai-project'",
                    "5. Create the project"
                ]
            },
            {
                "step": 2,
                "title": "Create Service Account",
                "actions": [
                    "1. Go to IAM & Admin → Service Accounts",
                    "2. Click 'Create Service Account'",
                    "3. Name: 'railway-personal'",
                    "4. Role: 'Editor' or 'Owner'",
                    "5. Create JSON key",
                    "6. Download the JSON file"
                ]
            },
            {
                "step": 3,
                "title": "Enable APIs",
                "actions": [
                    "1. Go to APIs & Services → Library",
                    "2. Enable 'Vertex AI API'",
                    "3. Enable 'Generative AI API'",
                    "4. No billing required for personal projects with free quotas!"
                ]
            },
            {
                "step": 4,
                "title": "Update Railway Environment",
                "actions": [
                    "1. Copy the JSON content",
                    "2. Update GOOGLE_SERVICE_ACCOUNT_JSON in Railway",
                    "3. Add GOOGLE_CLOUD_PROJECT with your project ID"
                ]
            }
        ],
        "why_this_works": [
            "Personal Google accounts get free quotas",
            "No billing setup required for basic usage",
            "Service accounts work better than OAuth on servers",
            "You control the project and permissions"
        ]
    }

@app.route('/test-with-project', methods=['POST'])
def test_with_project():
    """Test Gemini with personal project"""
    try:
        data = request.get_json()
        project_id = data.get('project_id', '')
        prompt = data.get('prompt', 'Write a Python hello world program')
        
        if not project_id:
            return {
                "success": False,
                "error": "Please provide your project_id",
                "example": {"project_id": "your-personal-project-id", "prompt": "your question"}
            }
        
        # Setup service account if available
        service_account_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
        if service_account_json:
            with open('service-account.json', 'w') as f:
                f.write(service_account_json)
            
            subprocess.run([
                'gcloud', 'auth', 'activate-service-account', 
                '--key-file=service-account.json'
            ], capture_output=True, text=True, timeout=15)
            
            subprocess.run([
                'gcloud', 'config', 'set', 'project', project_id
            ], capture_output=True, text=True, timeout=10)
        
        # Get access token
        token_result = subprocess.run([
            'gcloud', 'auth', 'print-access-token'
        ], capture_output=True, text=True, timeout=10)
        
        if token_result.returncode != 0:
            return {
                "success": False,
                "error": "Authentication failed. Please update GOOGLE_SERVICE_ACCOUNT_JSON with your personal project service account",
                "token_error": token_result.stderr
            }
        
        access_token = token_result.stdout.strip()
        
        # Call Gemini API with personal project
        url = f'https://us-central1-aiplatform.googleapis.com/v1/projects/{project_id}/locations/us-central1/publishers/google/models/gemini-pro:generateContent'
        
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
                    "response": ai_response,
                    "model": "gemini-pro",
                    "project": project_id
                }
        
        return {
            "success": False,
            "status_code": response.status_code,
            "error": response.text,
            "project": project_id
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/free-alternative')
def free_alternative():
    """Free AI alternative while you set up personal project"""
    return {
        "message": "While you set up your personal Google Cloud project, use these free alternatives:",
        "alternatives": [
            {
                "name": "Groq AI",
                "description": "Free Llama models - 100 requests/day",
                "signup": "https://console.groq.com/",
                "api_key_needed": True
            },
            {
                "name": "Hugging Face",
                "description": "Free AI models",
                "signup": "https://huggingface.co/",
                "api_key_needed": True
            },
            {
                "name": "Cohere",
                "description": "Free AI API - 100 requests/month",
                "signup": "https://cohere.ai/",
                "api_key_needed": True
            }
        ],
        "working_now": [
            "Translation API (MyMemory) - working",
            "Sentiment Analysis - working",
            "Simple rule-based AI - working"
        ]
    }

@app.route('/current-status')
def current_status():
    """Show current authentication status"""
    try:
        # Check service account
        service_account_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
        has_service_account = bool(service_account_json)
        
        if has_service_account:
            # Try to parse the service account to get project info
            try:
                sa_data = json.loads(service_account_json)
                current_project = sa_data.get('project_id', 'Unknown')
            except:
                current_project = 'Invalid JSON'
        else:
            current_project = 'No service account'
        
        # Test gcloud
        result = subprocess.run(['gcloud', 'auth', 'list'], 
                              capture_output=True, text=True, timeout=10)
        
        return {
            "service_account_available": has_service_account,
            "current_project": current_project,
            "gcloud_auth": result.stdout,
            "recommendation": "Create personal Google Cloud project to bypass OAuth issues"
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.route('/health')
def health():
    return {
        "status": "healthy",
        "platform": "Railway",
        "solution": "Create personal Google Cloud project",
        "oauth_issue": "Known gcloud CLI bug on servers"
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
