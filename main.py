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
    return "Google ML APIs on Railway - Using correct commands!"

@app.route('/translate', methods=['POST'])
def google_translate():
    """Use Google Translate API with correct command"""
    try:
        setup_and_activate_service_account()
        
        data = request.get_json()
        text = data.get('text', 'Hello world')
        target = data.get('target', 'es')  # Spanish by default
        
        result = subprocess.run([
            'gcloud', 'beta', 'ml', 'translate', 'translate-text',
            '--content', text,
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

@app.route('/language/sentiment', methods=['POST'])
def analyze_sentiment():
    """Analyze sentiment using Google Natural Language API"""
    try:
        setup_and_activate_service_account()
        
        data = request.get_json()
        text = data.get('text', 'I love this product!')
        
        result = subprocess.run([
            'gcloud', 'ml', 'language', 'analyze-sentiment',
            '--content', text,
            '--format', 'json'
        ], capture_output=True, text=True, timeout=20)
        
        return {
            "success": result.returncode == 0,
            "input": text,
            "output": result.stdout,
            "error": result.stderr
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/language/entities', methods=['POST'])
def analyze_entities():
    """Extract entities using Google Natural Language API"""
    try:
        setup_and_activate_service_account()
        
        data = request.get_json()
        text = data.get('text', 'Google was founded in California by Larry Page and Sergey Brin.')
        
        result = subprocess.run([
            'gcloud', 'ml', 'language', 'analyze-entities',
            '--content', text,
            '--format', 'json'
        ], capture_output=True, text=True, timeout=20)
        
        return {
            "success": result.returncode == 0,
            "input": text,
            "output": result.stdout,
            "error": result.stderr
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/language/classify', methods=['POST'])
def classify_text():
    """Classify text using Google Natural Language API"""
    try:
        setup_and_activate_service_account()
        
        data = request.get_json()
        text = data.get('text', 'This is a great movie with excellent acting and cinematography.')
        
        result = subprocess.run([
            'gcloud', 'ml', 'language', 'classify-text',
            '--content', text,
            '--format', 'json'
        ], capture_output=True, text=True, timeout=20)
        
        return {
            "success": result.returncode == 0,
            "input": text,
            "output": result.stdout,
            "error": result.stderr
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/translate/detect', methods=['POST'])
def detect_language():
    """Detect language using Google Translate API"""
    try:
        setup_and_activate_service_account()
        
        data = request.get_json()
        text = data.get('text', 'Bonjour le monde')
        
        result = subprocess.run([
            'gcloud', 'beta', 'ml', 'translate', 'detect-language',
            '--content', text,
            '--format', 'json'
        ], capture_output=True, text=True, timeout=20)
        
        return {
            "success": result.returncode == 0,
            "input": text,
            "output": result.stdout,
            "error": result.stderr
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/translate/languages')
def supported_languages():
    """Get supported languages for translation"""
    try:
        setup_and_activate_service_account()
        
        result = subprocess.run([
            'gcloud', 'beta', 'ml', 'translate', 'get-supported-languages',
            '--format', 'json'
        ], capture_output=True, text=True, timeout=20)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/available-commands')
def available_commands():
    """List all available ML commands"""
    return {
        "translation": [
            "POST /translate - Translate text",
            "POST /translate/detect - Detect language",
            "GET /translate/languages - Get supported languages"
        ],
        "natural_language": [
            "POST /language/sentiment - Analyze sentiment",
            "POST /language/entities - Extract entities", 
            "POST /language/classify - Classify text"
        ],
        "examples": {
            "translate": {"text": "Hello world", "target": "es"},
            "sentiment": {"text": "I love this product!"},
            "entities": {"text": "Google was founded in California"},
            "classify": {"text": "This is a great movie"}
        }
    }

@app.route('/health')
def health():
    return {
        "status": "healthy",
        "platform": "Railway",
        "gcloud": "authenticated",
        "ml_apis_available": True
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
