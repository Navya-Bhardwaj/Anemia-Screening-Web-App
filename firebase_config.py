import firebase_admin
from firebase_admin import credentials, auth, firestore
import os

# Firebase Configuration
# Note: You need to download your service account key from Firebase Console
# and place it in the same directory as 'serviceAccountKey.json'

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    try:
        # Check if already initialized
        if firebase_admin._apps:
            print("✅ Firebase already initialized")
            return True
            
        # Check if service account key exists
        service_key_path = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
        
        if os.path.exists(service_key_path):
            cred = credentials.Certificate(service_key_path)
            firebase_admin.initialize_app(cred, {
                'projectId': 'anemia-screening-tool',
                'storageBucket': 'anemia-screening-tool.firebasestorage.app'
            })
            print("✅ Firebase initialized successfully")
            return True
        else:
            print("❌ Service account key not found. Please download from Firebase Console")
            print("📁 Place 'serviceAccountKey.json' in the project directory")
            return False
    except Exception as e:
        print(f"❌ Firebase initialization failed: {e}")
        return False

def get_firestore_db():
    """Get Firestore database instance"""
    try:
        db = firestore.client()
        return db
    except Exception as e:
        print(f"❌ Firestore connection failed: {e}")
        return None

def create_user(email, password, display_name=None):
    """Create a new user in Firebase Auth"""
    try:
        user = auth.create_user(
            email=email,
            password=password,
            display_name=display_name
        )
        print(f"✅ Successfully created user: {user.uid}")
        return user
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return None

def verify_user_token(id_token):
    """Verify Firebase ID token"""
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        print(f"❌ Token verification failed: {e}")
        return None

def get_user_by_uid(uid):
    """Get user data by UID"""
    try:
        user = auth.get_user(uid)
        return user
    except Exception as e:
        print(f"❌ Error getting user: {e}")
        return None

# Initialize Firebase when module is imported
firebase_initialized = initialize_firebase()
