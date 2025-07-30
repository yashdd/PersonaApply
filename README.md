# PersonaApply 🚀

AI-Based Outreach Personalization — Tailored cover letters, cold emails, and LinkedIn reachouts. Built using Python, FastAPI, Langchain, and Firebase.

## 🎯 Overview

PersonaApply is an intelligent application that helps users generate personalized professional content by leveraging their background information stored as RAG (Retrieval-Augmented Generation) data. The system combines user profiles, uploaded documents, and AI to create tailored cover letters, cold emails, and LinkedIn messages.

## 🔄 User Flow

1. **Authentication**: Users register/login using Firebase Authentication
2. **Profile Setup**: First-time users upload their professional information (resume, GitHub, LinkedIn, portfolio)
3. **RAG Storage**: All user data is processed and stored in a vector database for intelligent retrieval
4. **Content Generation**: Users paste job descriptions or situations to generate personalized content using LLM + RAG

## 🏗️ Architecture

- **Backend**: FastAPI with async support
- **Authentication**: Firebase Admin SDK
- **AI/LLM**: Google Gemini Pro
- **Vector Database**: ChromaDB with sentence transformers
- **Frontend**: Streamlit (demo interface)
- **File Storage**: Local file system with metadata tracking

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Firebase project with Admin SDK credentials
- Google Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd PersonaApply
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` with your actual credentials:
   ```env
   # Gemini API Configuration
   GOOGLE_API_KEY=your_actual_gemini_api_key
   
   # Firebase Configuration
   FIREBASE_PROJECT_ID=your_firebase_project_id
   FIREBASE_PRIVATE_KEY_ID=your_firebase_private_key_id
   FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nyour_actual_private_key\n-----END PRIVATE KEY-----\n"
   FIREBASE_CLIENT_EMAIL=your_firebase_client_email
   FIREBASE_CLIENT_ID=your_firebase_client_id
   FIREBASE_CLIENT_X509_CERT_URL=your_firebase_client_x509_cert_url
   ```

4. **Run the FastAPI backend**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Run the Streamlit frontend** (in a new terminal)
   ```bash
   streamlit run streamlit_app.py
   ```

## 📚 API Endpoints

### Authentication
- `POST /auth/verify` - Verify Firebase token and get user info

### User Profile
- `GET /user/profile` - Get current user profile
- `PUT /user/profile` - Update user profile

### Document Management
- `POST /user/documents/upload` - Upload user document
- `GET /user/documents` - Get all user documents
- `DELETE /user/documents/{document_id}` - Delete user document

### Content Generation
- `POST /content/generate` - Generate single content type
- `POST /content/generate-all` - Generate all content types

## 🔧 Configuration

### Firebase Setup

1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
2. Enable Authentication (Email/Password or Google)
3. Go to Project Settings > Service Accounts
4. Generate a new private key
5. Use the downloaded JSON credentials in your `.env` file

### Google Gemini Setup

1. Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Add the key to your `.env` file

## 📁 Project Structure

```
PersonaApply/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── models.py            # Pydantic models
│   ├── auth.py              # Firebase authentication
│   ├── services/
│   │   ├── __init__.py
│   │   ├── user_service.py  # User profile management
│   │   └── content_service.py # Content generation
│   └── rag/
│       ├── __init__.py
│       └── vectorstore.py   # ChromaDB integration
├── streamlit_app.py         # Demo frontend
├── requirements.txt         # Python dependencies
├── env.example             # Environment template
└── README.md               # This file
```

## 🎨 Features

### User Management
- Firebase authentication integration
- User profile creation and updates
- Professional information tracking

### Document Processing
- Multi-format document upload (PDF, DOCX, TXT, MD)
- Automatic text extraction and processing
- Vector storage for intelligent retrieval

### Content Generation
- **Cover Letters**: Professional, tailored to job descriptions
- **Cold Emails**: Engaging outreach messages
- **LinkedIn Messages**: Connection requests and follow-ups
- **Personalization**: Uses user's background and documents
- **Tone Control**: Professional, friendly, formal, casual

### RAG Integration
- User-specific document storage
- Intelligent context retrieval
- Semantic search capabilities

## 🔒 Security

- Firebase JWT token verification
- User-specific data isolation
- Secure file upload handling
- Environment variable configuration

## 🚀 Deployment

### Local Development
```bash
# Backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend
streamlit run streamlit_app.py
```

### Production Considerations
- Use proper database (PostgreSQL, MongoDB)
- Implement proper file storage (AWS S3, Google Cloud Storage)
- Add rate limiting and monitoring
- Use HTTPS and proper CORS configuration
- Implement proper error handling and logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `http://localhost:8000/docs`
- Review the FastAPI interactive docs at `http://localhost:8000/redoc`
