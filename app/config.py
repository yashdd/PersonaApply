import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    app_name: str = "PersonaApply"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    # API Keys
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    huggingface_api_key: str = os.getenv("HUGGINGFACE_API_KEY", "")
    
    # Firebase Configuration
    firebase_project_id: str = os.getenv("FIREBASE_PROJECT_ID", "")
    firebase_private_key_id: str = os.getenv("FIREBASE_PRIVATE_KEY_ID", "")
    firebase_private_key: str = os.getenv("FIREBASE_PRIVATE_KEY", "")
    firebase_client_email: str = os.getenv("FIREBASE_CLIENT_EMAIL", "")
    firebase_client_id: str = os.getenv("FIREBASE_CLIENT_ID", "")
    firebase_auth_uri: str = os.getenv("FIREBASE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth")
    firebase_token_uri: str = os.getenv("FIREBASE_TOKEN_URI", "https://oauth2.googleapis.com/token")
    firebase_auth_provider_x509_cert_url: str = os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL", "https://www.googleapis.com/oauth2/v1/certs")
    firebase_client_x509_cert_url: str = os.getenv("FIREBASE_CLIENT_X509_CERT_URL", "")
    firebase_web_api_key: str = Field(..., description="FIREBASE_WEB_API_KEY")
    # Grok API
    grok_api_key: str = os.getenv("GROK_API_KEY", "")
    grok_api_url: str = os.getenv("GROK_API_URL", "https://api.grok.x.ai/v1/chat/completions")
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./personaapply.db")
    

    
    # File Upload Configuration
    upload_dir: str = os.getenv("UPLOAD_DIR", "./uploads")
    max_file_size: int = int(os.getenv("MAX_FILE_SIZE", "10485760")) 
    
    class Config:
        env_file = ".env"
        extra = "ignore"

# Global settings instance
settings = Settings() 