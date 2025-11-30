import firebase_admin
from firebase_admin import firestore, credentials
from ..config import FIREBASE_CREDENTIALS_PATH, FIREBASE_STORAGE_BUCKET

def initialize_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(str(FIREBASE_CREDENTIALS_PATH))
        firebase_admin.initialize_app(cred, {
            'storageBucket': FIREBASE_STORAGE_BUCKET
        })

initialize_firebase()
db = firestore.client()
