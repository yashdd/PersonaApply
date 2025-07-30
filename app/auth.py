import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import json
from .config import settings
import jwt

# Initialize Firebase Admin SDK
def initialize_firebase():
    """Initialize Firebase Admin SDK with credentials"""
    try:
        # Check if Firebase is already initialized
        try:
            firebase_admin.get_app()
            print("Firebase already initialized")
            return True
        except ValueError:
            pass
        
        # Create credentials dictionary from environment variables
        cred_dict = {
            "type": "service_account",
            "project_id": settings.firebase_project_id,
            "private_key_id": settings.firebase_private_key_id,
            "private_key": settings.firebase_private_key.replace("\\n", "\n"),
            "client_email": settings.firebase_client_email,
            "client_id": settings.firebase_client_id,
            "auth_uri": settings.firebase_auth_uri,
            "token_uri": settings.firebase_token_uri,
            "auth_provider_x509_cert_url": settings.firebase_auth_provider_x509_cert_url,
            "client_x509_cert_url": settings.firebase_client_x509_cert_url
        }
        
        cred = credentials.Certificate(cred_dict)
        
        # Initialize with explicit project ID
        firebase_admin.initialize_app(cred, {
            'projectId': settings.firebase_project_id
        })
        
        print(f"Firebase initialized successfully for project: {settings.firebase_project_id}")
        return True
    except Exception as e:
        print(f"Firebase initialization error: {e}")
        return False

# Security scheme for JWT tokens
security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    print("[DEBUG] Token received in verify_token:", credentials.credentials)
    try:
        token = credentials.credentials
        decoded_token = auth.verify_id_token(token)
        print("[DEBUG] Decoded token:", decoded_token)
        return decoded_token
    except Exception as e:
        print("[DEBUG] Token verification failed:", e)
        raise HTTPException(status_code=401, detail="Invalid authentication token")

async def get_current_user(token_data: dict = Depends(verify_token)) -> dict:
    """Get current authenticated user"""
    return {
        "uid": token_data.get("uid"),
        "email": token_data.get("email"),
        "name": token_data.get("name"),
        "picture": token_data.get("picture")
    }

def create_custom_token(uid: str) -> str:
    """Create a custom token for a user"""
    try:
        custom_token = auth.create_custom_token(uid)
        return custom_token.decode()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating custom token: {str(e)}")

def verify_id_token(token: str) -> dict:
    """Verify Firebase ID token or custom token"""
    try:
        # First try to verify as ID token
        try:
            decoded_token = auth.verify_id_token(token)
            return decoded_token
        except:
            # If ID token verification fails, try as custom token
            # For custom tokens, we need to exchange them for ID tokens
            # This is a simplified approach - in production you'd use Firebase Auth client
            try:
                # For now, we'll create a mock user from the custom token
                # In a real implementation, you'd exchange the custom token for an ID token
                # using the Firebase Auth client
                
                # Extract UID from custom token (this is a simplified approach)
                # In production, you'd use Firebase Auth client to exchange tokens
                decoded_custom = jwt.decode(token, options={"verify_signature": False})
                
                # Create a mock user data structure
                user_data = {
                    "uid": decoded_custom.get("uid", "unknown"),
                    "email": decoded_custom.get("email", "demo@example.com"),
                    "name": decoded_custom.get("name", "Demo User"),
                    "picture": decoded_custom.get("picture", "")
                }
                
                return user_data
                
            except Exception as custom_error:
                raise HTTPException(status_code=401, detail=f"Invalid token: {str(custom_error)}")
                
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

# Initialize Firebase on module import
initialize_firebase() 