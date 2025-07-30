from typing import Optional
from ..models import ContentType, ContentGenerationRequest, ContentGenerationResponse
from ..config import settings
from ..rag import VectorStore
import google.generativeai as genai

class ContentService:
    def __init__(self):
        self.vector_store = VectorStore()
        # Configure Google Gemini
        if settings.google_api_key:
            genai.configure(api_key=settings.google_api_key)
    
    def _get_content_prompt(self, content_type: ContentType, user_context: str, request: ContentGenerationRequest) -> str:
        """Generate appropriate prompt based on content type"""
        base_context = f"""
        User Context (from their documents):
        {user_context}
        
        Job Description/Situation:
        {request.job_description}
        
        Target Company: {request.target_company or 'Not specified'}
        Target Role: {request.target_role or 'Not specified'}
        Additional Context: {request.additional_context or 'None'}
        Tone: {request.tone}
        """
        
        if content_type == ContentType.COVER_LETTER:
            return f"""Write a professional cover letter based on this information:
\n{base_context}\nThe cover letter should be professional, highlight relevant skills, and be about 300-400 words. Use a {request.tone} tone.\nCover Letter:"""
        elif content_type == ContentType.COLD_EMAIL:
            return f"""Write a professional cold email based on this information:
\n{base_context}\nThe cold email should be concise (150-200 words), have a compelling subject line, and use a {request.tone} tone.\nCold Email:"""
        elif content_type == ContentType.LINKEDIN_MESSAGE:
            return f"""Write a professional LinkedIn message based on this information:
\n{base_context}\nThe LinkedIn message should be brief (max 300 characters), professional, and use a {request.tone} tone.\nLinkedIn Message:"""
        return f"""Generate professional content based on this information:\n{base_context}\nContent:"""
    
    async def _call_gemini_api(self, prompt: str) -> str:
        """Call the Google Gemini API to generate content from a prompt."""
        try:
            # Check if API key is configured
            if not settings.google_api_key:
                # Fallback to basic content generation
                return self._generate_fallback_content(prompt)
            
            # Use Gemini 1.5 Pro - the most advanced model
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content(prompt)
            
            if response.text:
                return response.text
            else:
                raise Exception("No content generated from Gemini API")
                
        except Exception as e:
            # Fallback if API fails
            print(f"API Error: {str(e)}. Using fallback content generation.")
            return self._generate_fallback_content(prompt)
    
    def _generate_fallback_content(self, prompt: str) -> str:
        """Generate basic fallback content when API is not available."""
        if "cover letter" in prompt.lower():
            return """Dear Hiring Manager,

I am writing to express my strong interest in the position. Based on my background and the job requirements, I believe I would be an excellent fit for this role.

My experience and skills align well with what you're looking for. I am excited about the opportunity to contribute to your team and would welcome the chance to discuss how I can add value to your organization.

Thank you for considering my application. I look forward to hearing from you.

Best regards,
[Your Name]"""
        
        elif "cold email" in prompt.lower():
            return """Subject: Quick Question About [Company/Project]

Hi [Name],

I hope this email finds you well. I came across your work at [Company] and was impressed by [specific detail].

I'm reaching out because [specific reason/connection]. I'd love to learn more about [specific topic] and see if there might be opportunities to collaborate or connect.

Would you be available for a brief call next week?

Best regards,
[Your Name]"""
        
        elif "linkedin message" in prompt.lower():
            return """Hi [Name],

I came across your profile and was impressed by your work at [Company]. I'd love to connect and learn more about your experience in [industry/field].

Best regards,
[Your Name]"""
        
        else:
            return "Content generation is currently using fallback mode. Please configure your Google API key for full functionality."
    
    async def generate_content(self, uid: str, request: ContentGenerationRequest) -> ContentGenerationResponse:
        """Generate personalized content using RAG context and Gemini API"""
        try:
            # Get user's RAG context
            user_context = await self.vector_store.get_user_context(uid)
            # Generate prompt
            prompt = self._get_content_prompt(request.content_type, user_context, request)
            # Call Gemini API
            generated_content = await self._call_gemini_api(prompt)
            # Enforce LinkedIn message length
            if request.content_type == ContentType.LINKEDIN_MESSAGE:
                generated_content = generated_content[:300]
            return ContentGenerationResponse(
                content_type=request.content_type,
                generated_content=generated_content,
                prompt_used=prompt,
                tokens_used=len(prompt + generated_content) // 4
            )
        except Exception as e:
            raise Exception(f"Error generating content: {str(e)}")

# Global content service instance
content_service = ContentService() 