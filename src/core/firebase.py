import firebase_admin
import json
import os
import streamlit as st
from firebase_admin import firestore, credentials
from ..config import FIREBASE_CREDENTIALS_PATH, FIREBASE_STORAGE_BUCKET

def initialize_firebase():
    if not firebase_admin._apps:
        # 1. Try loading from Streamlit Secrets (Deployment)
        if "FIREBASE_CREDENTIALS_JSON" in st.secrets:
            # st.secrets returns it as a string if defined as such in TOML
            secret_str = st.secrets["FIREBASE_CREDENTIALS_JSON"]
            try:
                cred_json = json.loads(secret_str)
            except json.JSONDecodeError:
                # Fallback: strict JSON requires double quotes and no trailing commas.
                # Sometimes copying into TOML adds extra escaping to \n.
                # Let's try to fix common issues.
                try:
                    # If the string has literal newlines instead of \n, replace them?
                    # Or if it has \\n that needs to be \n?
                    # Actually, often the issue is control characters.
                    # Let's try strict=False
                    cred_json = json.loads(secret_str, strict=False)
                except:
                    # Last resort: The user might have put the DICT directly in secrets.toml 
                    # [FIREBASE_CREDENTIALS_JSON]
                    # type = "service_account"
                    # ...
                    # In that case, st.secrets["FIREBASE_CREDENTIALS_JSON"] is ALREADY a dict (AttrDict).
                    if isinstance(secret_str, dict) or hasattr(secret_str, "type"):
                        cred_json = dict(secret_str)
                    else:
                        raise
            
            cred = credentials.Certificate(cred_json)
        
        # 2. Try loading from Environment Variable (Alternative)
        elif os.getenv("FIREBASE_CREDENTIALS_JSON"):
            cred_json = json.loads(os.getenv("FIREBASE_CREDENTIALS_JSON"))
            cred = credentials.Certificate(cred_json)
            
        # 3. Fallback to Local File (Development)
        else:
            cred = credentials.Certificate(str(FIREBASE_CREDENTIALS_PATH))
            
        firebase_admin.initialize_app(cred, {
            'storageBucket': FIREBASE_STORAGE_BUCKET
        })

initialize_firebase()
db = firestore.client()
