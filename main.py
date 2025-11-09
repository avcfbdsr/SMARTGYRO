from flask import Flask, jsonify, request
import subprocess
import os
import json
import requests

app = Flask(__name__)

@app.route('/')
def hello():
    return "Free AI Models on Railway - No billing required!"

@app.route('/ai/huggingface', methods=['POST'])
def huggingface_ai():
    """Use Hugging Face free AI models"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', 'Hello, how are you?')
        
        # Use Hugging Face Inference API (free)
        url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": 100,
                "temperature": 0.7
            }
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        return {
            "success": response.status_code == 200,
            "prompt": prompt,
            "response": response.json() if response.status_code == 200 else response.text,
            "model": "microsoft/DialoGPT-medium",
            "provider": "Hugging Face (Free)"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/ai/ollama', methods=['POST'])
def ollama_ai():
    """Use Ollama for local AI (if available)"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', 'Hello, how are you?')
        
        # Try to use Ollama (free, local AI)
        result = subprocess.run([
            'curl', '-X', 'POST', 'http://localhost:11434/api/generate',
            '-H', 'Content-Type: application/json',
            '-d', json.dumps({
                "model": "llama2",
                "prompt": prompt,
                "stream": False
            })
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return {
                "success": True,
                "prompt": prompt,
                "response": result.stdout,
                "model": "llama2",
                "provider": "Ollama (Local)"
            }
        else:
            return {
                "success": False,
                "error": "Ollama not available",
                "suggestion": "Install Ollama for local AI models"
            }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/ai/openai-free', methods=['POST'])
def openai_free():
    """Use OpenAI-compatible free APIs"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', 'Hello, how are you?')
        
        # Use a free OpenAI-compatible API
        url = "https://api.openai.com/v1/chat/completions"
        
        # Note: This requires an OpenAI API key
        # For demo purposes, returning a mock response
        return {
            "success": False,
            "error": "OpenAI API key required",
            "suggestion": "Add OPENAI_API_KEY environment variable for OpenAI access",
            "alternatives": [
                "Use /ai/huggingface for free AI",
                "Enable Google Cloud billing for Gemini",
                "Install Ollama for local AI"
            ]
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/billing/info')
def billing_info():
    """Information about enabling Google Cloud billing"""
    return {
        "message": "Google AI models require billing to be enabled",
        "steps": [
            "1. Go to Google Cloud Console",
            "2. Select project: peppy-bond-477619-a8", 
            "3. Go to Billing section",
            "4. Add payment method (credit card)",
            "5. Enable billing for the project",
            "6. Wait a few minutes for activation"
        ],
        "billing_url": "https://console.developers.google.com/billing/enable?project=peppy-bond-477619-a8",
        "free_alternatives": [
            "/ai/huggingface - Free Hugging Face models",
            "/ai/ollama - Local AI models (if installed)"
        ]
    }

@app.route('/health')
def health():
    return {
        "status": "healthy",
        "platform": "Railway", 
        "ai_options": [
            "Hugging Face (Free)",
            "Google Gemini (Requires billing)",
            "Ollama (Local, if installed)"
        ]
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
