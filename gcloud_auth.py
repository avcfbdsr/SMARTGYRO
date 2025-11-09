import os
import subprocess

def setup_gcloud_auth():
    """Setup Google Cloud authentication on app startup"""
    try:
        # Check if service account file exists
        if os.path.exists('service-account.json'):
            subprocess.run(['gcloud', 'auth', 'activate-service-account', '--key-file=service-account.json'], check=True)
            print("Google Cloud authenticated with service account")
        else:
            print("No service account file found - skipping gcloud auth")
    except Exception as e:
        print(f"Google Cloud auth failed: {e}")

# Call this at the start of your main app
setup_gcloud_auth()
