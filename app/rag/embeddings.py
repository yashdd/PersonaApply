"""
Text Embeddings Module

This module handles text embedding operations using HuggingFace models.
"""

from typing import List, Optional
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from .config import faiss_config


class EmbeddingService:
    """Service for handling text embeddings and chunking"""
    
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=faiss_config.embedding_model
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=faiss_config.chunk_size,
            chunk_overlap=faiss_config.chunk_overlap,
            length_function=len,
        )
    
    def get_embeddings(self) -> HuggingFaceEmbeddings:
        """Get the embedding model instance"""
        return self.embeddings
    
    def get_text_splitter(self) -> RecursiveCharacterTextSplitter:
        """Get the text splitter instance"""
        return self.text_splitter
    
    def split_text(self, text: str) -> List[str]:
        """Split text into chunks"""
        return self.text_splitter.split_text(text)
    
    def embed_text(self, text: str) -> List[float]:
        """Embed a single text string"""
        return self.embeddings.embed_query(text)
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple text strings"""
        return self.embeddings.embed_documents(texts)


# Global embedding service instance
embedding_service = EmbeddingService() 