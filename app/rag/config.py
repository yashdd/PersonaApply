"""
FAISS Vector Store Configuration

This module contains all configuration settings related to FAISS vector storage.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field


class FAISSConfig(BaseModel):
    """FAISS vector store configuration"""
    
    # Storage settings
    persist_directory: str = Field(
        default="./app/rag/data",
        description="Directory to store FAISS index and metadata"
    )
    
    # Embedding model settings
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="HuggingFace embedding model name"
    )
    
    # Text splitting settings
    chunk_size: int = Field(
        default=1000,
        description="Size of text chunks for vectorization"
    )
    
    chunk_overlap: int = Field(
        default=200,
        description="Overlap between text chunks"
    )
    
    # Search settings
    default_search_k: int = Field(
        default=5,
        description="Default number of results to return from search"
    )
    
    max_context_chunks: int = Field(
        default=10,
        description="Maximum number of chunks to include in context"
    )
    
    # Index settings
    index_name: str = Field(
        default="faiss_index",
        description="Name of the FAISS index directory"
    )
    
    documents_file: str = Field(
        default="documents.pkl",
        description="Name of the documents metadata file"
    )


# Global FAISS configuration instance
faiss_config = FAISSConfig() 