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
            cred_json = json.loads(st.secrets["FIREBASE_CREDENTIALS_JSON"])
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
