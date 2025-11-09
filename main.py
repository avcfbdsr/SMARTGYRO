from flask import Flask, jsonify
import subprocess
import os
import glob

app = Flask(__name__)

@app.route('/')
def hello():
    return "Google CLI installed and ready!"

@app.route('/debug')
def debug():
    # Find gcloud installation
    possible_paths = [
        "/opt/render/project/src/google-cloud-sdk/bin/gcloud",
        "/home/render/google-cloud-sdk/bin/gcloud", 
        "/root/google-cloud-sdk/bin/gcloud",
        "~/google-cloud-sdk/bin/gcloud"
    ]
    
    found_paths = []
    for path in possible_paths:
        expanded_path = os.path.expanduser(path)
        if os.path.exists(expanded_path):
            found_paths.append(expanded_path)
    
    # Also search for gcloud files
    gcloud_files = glob.glob("/*/google-cloud-sdk/bin/gcloud", recursive=True)
    gcloud_files.extend(glob.glob("/home/*/google-cloud-sdk/bin/gcloud"))
    
    return {
        "PATH": os.environ.get('PATH'),
        "HOME": os.environ.get('HOME'),
        "PWD": os.getcwd(),
        "found_paths": found_paths,
        "gcloud_files": gcloud_files,
        "ls_home": os.listdir(os.path.expanduser("~")) if os.path.exists(os.path.expanduser("~")) else "No home"
    }

@app.route('/gcloud/version')
def gcloud_version():
    # Try different gcloud paths
    gcloud_paths = [
        "gcloud",
        "/opt/render/project/src/google-cloud-sdk/bin/gcloud",
        "/home/render/google-cloud-sdk/bin/gcloud",
        os.path.expanduser("~/google-cloud-sdk/bin/gcloud")
    ]
    
    for gcloud_path in gcloud_paths:
        try:
            result = subprocess.run([gcloud_path, 'version'], capture_output=True, text=True, timeout=10)
            return {"path_used": gcloud_path, "output": result.stdout, "error": result.stderr}
        except Exception as e:
            continue
    
    return {"error": "gcloud not found in any expected location"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
