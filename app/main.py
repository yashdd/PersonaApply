from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from typing import List, Optional
import uvicorn
from pydantic import BaseModel

from .auth import get_current_user, verify_id_token
from .models import (
    UserProfile, UserDocument, ContentGenerationRequest, 
    ContentGenerationResponse, FileUploadResponse, AuthResponse,
    DocumentType, ContentType
)
from .services import user_service, content_service
from .config import settings

app = FastAPI(
    title="PersonaApply API",
    description="AI-Based Outreach Personalization API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
# class User(BaseModel):
#     name:str
#     age:int
#     email:str
    

# class Course(BaseModel):
#     title:str
#     duration_weeks:int


# class Registration(BaseModel):
#     referral_code:Optional[str]
#     user:User
#     course:Course

    

# @app.post("/registerr")
# def register(data: Registration):
#     return {"message": "Registration successful!", "data": data}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "PersonaApply API",
        "version": "1.0.0",
        "status": "running"
    }

@app.post("/auth/verify", response_model=AuthResponse)
async def verify_auth(token: str = Form(...)):
    """Verify Firebase token and get user info"""
    try:
        # Verify the token
        token_data = verify_id_token(token)
        
        # Get or create user
        user_data = {
            "uid": token_data.get("uid"),
            "email": token_data.get("email"),
            "name": token_data.get("name"),
            "picture": token_data.get("picture")
        }
        print(f"[DEBUG] About to call create_or_update_user with: {user_data}")

        user = await user_service.create_or_update_user(user_data)
        
        return AuthResponse(
            token=token,
            user=user,
            message="Authentication successful"
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.get("/user/profile", response_model=UserProfile)
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user's profile"""
    user = await user_service.get_user(current_user["uid"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/user/profile", response_model=UserProfile)
async def update_user_profile(
    profile_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update user profile"""
    user = await user_service.update_user_profile(current_user["uid"], profile_data)
    return user

@app.post("/user/documents/upload", response_model=FileUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    document_type: DocumentType = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload user document"""
    try:
        document = await user_service.upload_document(
            current_user["uid"], 
            file, 
            document_type
        )
        
        return FileUploadResponse(
            document_id=document.document_id,
            filename=document.filename,
            document_type=document.document_type,
            status="success",
            message="Document uploaded successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/user/documents", response_model=List[UserDocument])
async def get_user_documents(current_user: dict = Depends(get_current_user)):
    """Get all user documents"""
    documents = await user_service.get_user_documents(current_user["uid"])
    return documents

@app.delete("/user/documents/{document_id}")
async def delete_document(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete user document"""
    success = await user_service.delete_document(current_user["uid"], document_id)
    if success:
        return {"message": "Document deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Document not found")

@app.post("/content/generate", response_model=ContentGenerationResponse)
async def generate_content(
    request: ContentGenerationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate personalized content"""
    try:
        result = await content_service.generate_content(current_user["uid"], request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/content/generate-all")
async def generate_all_content(
    request: ContentGenerationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate all types of content (cover letter, cold email, LinkedIn message)"""
    try:
        results = await content_service.generate_multiple_content(current_user["uid"], request)
        return {
            "user_id": current_user["uid"],
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    ) 