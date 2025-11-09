from flask import Flask
from gcloud_auth import setup_gcloud_auth

# Setup Google Cloud authentication
setup_gcloud_auth()

app = Flask(__name__)

@app.route('/')
def hello():
    return "Google CLI installed and ready!"

@app.route('/health')
def health():
    return {"status": "healthy", "gcloud": "installed"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
