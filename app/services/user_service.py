import os
import uuid
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, UploadFile
import aiofiles
from ..models import UserProfile, UserDocument, DocumentType
from ..config import settings
from ..rag import VectorStore
from firebase_admin import firestore

class UserService:
    def __init__(self):
        self.vector_store = VectorStore()
        self.db = firestore.client()

    # --- User methods ---
    async def create_or_update_user(self, user_data: dict) -> UserProfile:
        """Create or update a user (basic info only)"""
        uid = user_data["uid"]
        doc_ref = self.db.collection("users").document(uid)
        doc_ref.set(user_data, merge=True)
        return await self.get_user(uid)

    async def get_user(self, uid: str) -> Optional[UserProfile]:
        doc_ref = self.db.collection("users").document(uid)
        doc = doc_ref.get()
        if doc.exists:
            return UserProfile(**doc.to_dict())
        return None

    async def update_user(self, uid: str, update_data: dict) -> UserProfile:
        """Update user details (basic info only)"""
        doc_ref = self.db.collection("users").document(uid)
        doc_ref.update(update_data)
        return await self.get_user(uid)

    async def delete_user(self, uid: str) -> bool:
        """Delete user and all their documents"""
        # Delete user document
        doc_ref = self.db.collection("users").document(uid)
        doc_ref.delete()
        # Delete all user documents
        docs = self.db.collection("user_documents").where("uid", "==", uid).stream()
        for doc in docs:
            await self.delete_document(uid, doc.id)
        return True

    # --- Document methods ---
    async def upload_document(self, uid: str, file: UploadFile, document_type: DocumentType) -> UserDocument:
        if file.size and file.size > settings.max_file_size:
            raise HTTPException(status_code=400, detail="File too large")
        document_id = str(uuid.uuid4())
        file_path = os.path.join(settings.upload_dir, f"{document_id}_{file.filename}")
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        text_content = await self._extract_text(file_path, file.filename)
        document = UserDocument(
            uid=uid,
            document_id=document_id,
            document_type=document_type,
            filename=file.filename,
            content=text_content,
            metadata={
                "file_path": file_path,
                "file_size": len(content),
                "content_type": file.content_type
            }
        )
        doc_ref = self.db.collection("user_documents").document(document_id)
        doc_ref.set(document.dict())
        await self.vector_store.add_document(
            document_id=document_id,
            content=text_content,
            metadata={
                "uid": uid,
                "document_type": document_type.value,
                "filename": file.filename
            }
        )
        return document

    async def _extract_text(self, file_path: str, filename: str) -> str:
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                return await f.read()
        except UnicodeDecodeError:
            return f"Document: {filename}"

    async def get_user_documents(self, uid: str) -> List[UserDocument]:
        docs = self.db.collection("user_documents").where("uid", "==", uid).stream()
        return [UserDocument(**doc.to_dict()) for doc in docs]

    async def delete_document(self, uid: str, document_id: str) -> bool:
        doc_ref = self.db.collection("user_documents").document(document_id)
        doc = doc_ref.get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Document not found")
        doc_data = doc.to_dict()
        await self.vector_store.delete_document(document_id)
        file_path = doc_data.get("metadata", {}).get("file_path")
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        doc_ref.delete()
        return True

    async def get_user_rag_context(self, uid: str) -> str:
        documents = await self.get_user_documents(uid)
        if not documents:
            return ""
        context_parts = []
        for doc in documents:
            context_parts.append(f"Document Type: {doc.document_type.value}")
            context_parts.append(f"Content: {doc.content}")
            context_parts.append("---")
        return "\n".join(context_parts)

# Global user service instance
user_service = UserService() 