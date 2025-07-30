from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime

class ContentType(str, Enum):
    COVER_LETTER = "cover_letter"
    COLD_EMAIL = "cold_email"
    LINKEDIN_MESSAGE = "linkedin_message"

class DocumentType(str, Enum):
    RESUME = "resume"
    GITHUB = "github"
    LINKEDIN = "linkedin"
    PORTFOLIO = "portfolio"
    OTHER = "other"

class UserProfile(BaseModel):
    """User profile model"""
    uid: str = Field(..., description="Firebase user ID")
    email: str = Field(..., description="User email")
    name: Optional[str] = Field(None, description="User name")
    picture: Optional[str] = Field(None, description="Profile picture URL")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Profile information
    title: Optional[str] = Field(None, description="Professional title")
    summary: Optional[str] = Field(None, description="Professional summary")
    skills: List[str] = Field(default_factory=list, description="Skills list")
    experience_years: Optional[int] = Field(None, description="Years of experience")
    
    # Social links
    github_url: Optional[str] = Field(None, description="GitHub profile URL")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")
    portfolio_url: Optional[str] = Field(None, description="Portfolio website URL")

class UserDocument(BaseModel):
    """User document model for RAG storage"""
    uid: str = Field(..., description="Firebase user ID")
    document_id: str = Field(..., description="Unique document ID")
    document_type: DocumentType = Field(..., description="Type of document")
    filename: str = Field(..., description="Original filename")
    content: str = Field(..., description="Extracted text content")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ContentGenerationRequest(BaseModel):
    """Request model for content generation"""
    content_type: ContentType = Field(..., description="Type of content to generate")
    job_description: str = Field(..., description="Job description or situation")
    target_company: Optional[str] = Field(None, description="Target company name")
    target_role: Optional[str] = Field(None, description="Target role/title")
    additional_context: Optional[str] = Field(None, description="Additional context or requirements")
    tone: Optional[str] = Field("professional", description="Tone of the message")

class ContentGenerationResponse(BaseModel):
    """Response model for generated content"""
    content_type: ContentType
    generated_content: str
    prompt_used: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    tokens_used: Optional[int] = Field(None, description="Number of tokens used")

class FileUploadResponse(BaseModel):
    """Response model for file upload"""
    document_id: str
    filename: str
    document_type: DocumentType
    status: str
    message: str

class AuthResponse(BaseModel):
    """Authentication response model"""
    token: str
    user: UserProfile
    message: str

class ToneType(str, Enum):
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    CONFIDENT = "confident"
    ENTHUSIASTIC = "enthusiastic"
    FORMAL = "formal"

class GenerateRequest(BaseModel):
    """Request model for content generation"""
    content_type: ContentType
    job_title: str = Field(..., description="Target job title or position")
    company_name: str = Field(..., description="Target company name")
    recipient_name: Optional[str] = Field(None, description="Recipient's name if known")
    recipient_role: Optional[str] = Field(None, description="Recipient's role/title")
    user_experience: str = Field(..., description="User's relevant experience and background")
    user_skills: List[str] = Field(..., description="User's key skills")
    tone: ToneType = Field(ToneType.PROFESSIONAL, description="Desired tone of the message")
    additional_context: Optional[str] = Field(None, description="Additional context or specific requirements")
    max_length: Optional[int] = Field(500, description="Maximum length of the generated content")

class GenerateResponse(BaseModel):
    """Response model for generated content"""
    content: str
    content_type: ContentType
    metadata: Dict[str, Any] = Field(default_factory=dict)
    suggestions: List[str] = Field(default_factory=list)

class CompanyInfo(BaseModel):
    """Model for company information"""
    name: str
    industry: Optional[str] = None
    description: Optional[str] = None
    values: Optional[List[str]] = None
    recent_news: Optional[List[str]] = None

class JobInfo(BaseModel):
    """Model for job information"""
    title: str
    company: str
    description: Optional[str] = None
    requirements: Optional[List[str]] = None
    responsibilities: Optional[List[str]] = None

class RAGQuery(BaseModel):
    """Model for RAG queries"""
    query: str
    content_type: ContentType
    company_context: Optional[CompanyInfo] = None
    job_context: Optional[JobInfo] = None 