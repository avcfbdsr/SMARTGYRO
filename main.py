from flask import Flask, jsonify
import subprocess
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return "Google CLI installed and ready!"

@app.route('/gcloud/version')
def gcloud_version():
    try:
        result = subprocess.run(['gcloud', 'version'], capture_output=True, text=True)
        return {"output": result.stdout, "error": result.stderr}
    except Exception as e:
        return {"error": str(e)}

@app.route('/test')
def test():
    return {"status": "working", "path": os.environ.get('PATH')}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
