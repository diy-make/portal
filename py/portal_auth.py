import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# --- CONFIGURATION ---
# We need cloud-platform scope for Vertex AI (Imagen 3)
SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_DIR = os.path.join(BASE_DIR, 'secret')
TOKEN_PATH = os.path.join(SECRET_DIR, 'portal_token.json')

def get_client_secret_path():
    """Finds the first client_secret JSON in the secret directory."""
    if not os.path.exists(SECRET_DIR):
        return None
    for f in os.listdir(SECRET_DIR):
        if f.startswith("client_secret") and f.endswith(".json"):
            return os.path.join(SECRET_DIR, f)
    return None

def authenticate_portal():
    """Handles OAuth flow for the Portal project and persists the token."""
    creds = None
    
    # 1. Try loading existing token
    if os.path.exists(TOKEN_PATH):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
            print("✔ Found existing portal token.")
        except Exception as e:
            print(f"⚠ Failed to load existing token: {e}")

    # 2. Refresh or run flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                print("🔄 Refreshing portal token...")
                creds.refresh(Request())
            except Exception as e:
                print(f"❌ Refresh failed: {e}")
                creds = None
        
        if not creds:
            client_secret_path = get_client_secret_path()
            if not client_secret_path:
                print(f"❌ Error: No client_secret JSON found in '{SECRET_DIR}'")
                return None
            
            print(f"🚀 Initiating new authentication flow using {os.path.basename(client_secret_path)}...")
            # run_local_server will open a browser window
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # 3. Save the credentials for the next run
        with open(TOKEN_PATH, "w") as token_file:
            token_file.write(creds.to_json())
            print(f"💾 Portal token secured at {TOKEN_PATH}")
    
    return creds

if __name__ == "__main__":
    creds = authenticate_portal()
    if creds:
        print("\n--- 🔱 Portal Substrate Authenticated ---")
        print(f"Project: {creds.quota_project_id if hasattr(creds, 'quota_project_id') else 'Unknown'}")
        print("Status: READY FOR IMAGEN STRIKES")
        print("-----------------------------------------")
