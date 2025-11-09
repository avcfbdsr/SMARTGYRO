from flask import Flask, jsonify, request
import subprocess
import os
import json
import requests

app = Flask(__name__)

@app.route('/')
def hello():
    return "100% Free AI APIs - No billing required!"

@app.route('/ai/huggingface', methods=['POST'])
def huggingface_ai():
    """Use Hugging Face free AI models"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', 'Hello, how are you?')
        
        # Use Hugging Face Inference API (completely free)
        url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
        
        headers = {"Content-Type": "application/json"}
        payload = {"inputs": prompt}
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        return {
            "success": response.status_code == 200,
            "prompt": prompt,
            "response": response.json() if response.status_code == 200 else response.text,
            "model": "microsoft/DialoGPT-medium",
            "provider": "Hugging Face (100% Free)"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/translate/free', methods=['POST'])
def free_translate():
    """Free translation using MyMemory API"""
    try:
        data = request.get_json()
        text = data.get('text', 'Hello world')
        target = data.get('target', 'es')
        
        # Use MyMemory free translation API
        url = f"https://api.mymemory.translated.net/get?q={text}&langpair=en|{target}"
        
        response = requests.get(url, timeout=10)
        result = response.json()
        
        return {
            "success": response.status_code == 200,
            "input": text,
            "target_language": target,
            "translation": result.get('responseData', {}).get('translatedText', 'Translation failed'),
            "provider": "MyMemory (100% Free)"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/sentiment/free', methods=['POST'])
def free_sentiment():
    """Free sentiment analysis using TextBlob-like approach"""
    try:
        data = request.get_json()
        text = data.get('text', 'I love this product!')
        
        # Simple sentiment analysis using word matching
        positive_words = ['love', 'great', 'awesome', 'excellent', 'good', 'amazing', 'wonderful', 'fantastic']
        negative_words = ['hate', 'bad', 'terrible', 'awful', 'horrible', 'worst', 'disgusting']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = "POSITIVE"
            score = 0.7
        elif negative_count > positive_count:
            sentiment = "NEGATIVE" 
            score = -0.7
        else:
            sentiment = "NEUTRAL"
            score = 0.0
            
        return {
            "success": True,
            "input": text,
            "sentiment": sentiment,
            "score": score,
            "positive_words_found": positive_count,
            "negative_words_found": negative_count,
            "provider": "Simple Word Matching (100% Free)"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/ai/openai-free', methods=['POST'])
def openai_free():
    """Use OpenAI-compatible free APIs"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', 'Hello, how are you?')
        
        # Use Groq free API (OpenAI-compatible)
        url = "https://api.groq.com/openai/v1/chat/completions"
        
        # This would need a free Groq API key
        return {
            "success": False,
            "message": "Add GROQ_API_KEY environment variable for free Groq AI",
            "alternative": "Use /ai/huggingface for completely free AI",
            "groq_signup": "https://console.groq.com/ - Free 100 requests/day"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/ai/local-llm', methods=['POST'])
def local_llm():
    """Information about running local LLMs"""
    return {
        "message": "Run AI models locally for 100% free usage",
        "options": [
            {
                "name": "Ollama",
                "description": "Run Llama, Mistral, etc. locally",
                "install": "curl -fsSL https://ollama.ai/install.sh | sh",
                "models": ["llama2", "mistral", "codellama"]
            },
            {
                "name": "GPT4All",
                "description": "Desktop app for local AI",
                "website": "https://gpt4all.io/"
            },
            {
                "name": "LM Studio", 
                "description": "Easy local AI interface",
                "website": "https://lmstudio.ai/"
            }
        ]
    }

@app.route('/free-services')
def free_services():
    """List all completely free AI services"""
    return {
        "completely_free": [
            {
                "service": "Hugging Face AI",
                "endpoint": "POST /ai/huggingface",
                "description": "Free AI text generation",
                "quota": "Unlimited (with rate limits)"
            },
            {
                "service": "MyMemory Translation",
                "endpoint": "POST /translate/free", 
                "description": "Free text translation",
                "quota": "1000 words/day free"
            },
            {
                "service": "Simple Sentiment Analysis",
                "endpoint": "POST /sentiment/free",
                "description": "Basic sentiment detection",
                "quota": "Unlimited"
            }
        ],
        "free_with_signup": [
            {
                "service": "Groq AI",
                "quota": "100 requests/day free",
                "signup": "https://console.groq.com/"
            },
            {
                "service": "Cohere AI",
                "quota": "100 requests/month free", 
                "signup": "https://cohere.ai/"
            }
        ]
    }

@app.route('/health')
def health():
    return {
        "status": "healthy",
        "platform": "Railway",
        "billing_required": False,
        "free_ai_available": True
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
