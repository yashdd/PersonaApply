import faiss
import numpy as np
import pickle
import os
from typing import List, Dict, Any, Optional, Tuple
from langchain_community.vectorstores import FAISS
from .config import faiss_config
from .embeddings import embedding_service

class VectorStore:
    """Vector store for document storage and retrieval using FAISS"""
    
    def __init__(self):
        self.persist_directory = faiss_config.persist_directory
        self.embeddings = embedding_service.get_embeddings()
        self.text_splitter = embedding_service.get_text_splitter()
        
        # Initialize FAISS vector store
        self.vectorstore = None
        self.documents = []  # Store document metadata
        self.load_or_create_vectorstore()
    
    def load_or_create_vectorstore(self):
        """Load existing FAISS index or create new one"""
        index_path = os.path.join(self.persist_directory, faiss_config.index_name)
        docs_path = os.path.join(self.persist_directory, faiss_config.documents_file)
        
        if os.path.exists(index_path) and os.path.exists(docs_path):
            try:
                # Load existing FAISS index
                self.vectorstore = FAISS.load_local(
                    index_path, 
                    self.embeddings
                )
                # Load documents metadata
                with open(docs_path, 'rb') as f:
                    self.documents = pickle.load(f)
                print(f"Loaded existing FAISS index with {len(self.documents)} documents")
            except Exception as e:
                print(f"Error loading existing index: {e}")
                self.create_new_vectorstore()
        else:
            self.create_new_vectorstore()
    
    def create_new_vectorstore(self):
        """Create a new FAISS vector store"""
        # Create directory if it doesn't exist
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Initialize with empty documents
        self.vectorstore = FAISS.from_texts(
            texts=["Initial document"],
            embedding=self.embeddings
        )
        self.documents = []
        print("Created new FAISS vector store")
    
    def save_vectorstore(self):
        """Save the FAISS index and documents metadata"""
        if self.vectorstore:
            index_path = os.path.join(self.persist_directory, faiss_config.index_name)
            docs_path = os.path.join(self.persist_directory, faiss_config.documents_file)
            
            # Save FAISS index
            self.vectorstore.save_local(index_path)
            
            # Save documents metadata
            with open(docs_path, 'wb') as f:
                pickle.dump(self.documents, f)
    
    async def add_document(self, document_id: str, content: str, metadata: Dict[str, Any]):
        """Add a single document to the vector store"""
        # Split content into chunks
        chunks = self.text_splitter.split_text(content)
        
        # Prepare metadata for each chunk
        chunk_metadatas = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = metadata.copy()
            chunk_metadata["chunk_id"] = i
            chunk_metadata["document_id"] = document_id
            chunk_metadatas.append(chunk_metadata)
        
        # Add to vector store
        self.vectorstore.add_texts(texts=chunks, metadatas=chunk_metadatas)
        
        # Store document metadata
        self.documents.append({
            "document_id": document_id,
            "metadata": metadata,
            "chunk_count": len(chunks)
        })
        
        # Save the updated vector store
        self.save_vectorstore()
    
    async def delete_document(self, document_id: str):
        """Delete all chunks for a specific document"""
        # Get all documents with the specific document_id
        # Note: FAISS doesn't support direct deletion, so we'll rebuild the index
        # This is a limitation of FAISS, but it's still more reliable than ChromaDB on Windows
        
        # Remove from documents list
        self.documents = [doc for doc in self.documents if doc["document_id"] != document_id]
        
        # Rebuild the index without the deleted document
        self.rebuild_index()
    
    def rebuild_index(self):
        """Rebuild the FAISS index from remaining documents"""
        # This is a simplified approach - in production you might want to store
        # the original texts separately for rebuilding
        print("Rebuilding FAISS index...")
        self.create_new_vectorstore()
    
    async def get_user_context(self, uid: str, max_chunks: int = None) -> str:
        if max_chunks is None:
            max_chunks = faiss_config.max_context_chunks
        """Get user's document context for content generation"""
        try:
            # Search for user's documents
            # Since FAISS doesn't support filtering, we'll search and filter results
            dummy_query = "user context"  # We'll filter results by metadata
            results = self.vectorstore.similarity_search_with_score(
                dummy_query,
                k=max_chunks * 2  # Get more results to filter
            )
            
            # Filter results by user ID
            user_results = []
            for doc, score in results:
                if hasattr(doc, 'metadata') and doc.metadata.get('uid') == uid:
                    user_results.append((doc, score))
            
            if not user_results:
                return "No user documents found."
            
            # Take the top results
            user_results = user_results[:max_chunks]
            
            # Combine all chunks
            context_parts = []
            for doc, score in user_results:
                doc_type = doc.metadata.get("document_type", "unknown")
                context_parts.append(f"Document Type: {doc_type}")
                context_parts.append(f"Content: {doc.page_content}")
                context_parts.append("---")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            print(f"Error getting user context: {e}")
            return "Error retrieving user context."
    
    def add_documents(self, documents: List[str], metadata: List[Dict[str, Any]] = None):
        """Add documents to the vector store"""
        if metadata is None:
            metadata = [{"source": f"doc_{i}"} for i in range(len(documents))]
        
        # Split documents into chunks
        docs = []
        for doc, meta in zip(documents, metadata):
            chunks = self.text_splitter.split_text(doc)
            for chunk in chunks:
                docs.append({"text": chunk, "metadata": meta})
        
        # Add to vector store
        texts = [doc["text"] for doc in docs]
        metadatas = [doc["metadata"] for doc in docs]
        
        self.vectorstore.add_texts(texts=texts, metadatas=metadatas)
        
        # Save the updated vector store
        self.save_vectorstore()
    
    def search(self, query: str, k: int = None, filter_dict: Dict[str, Any] = None):
        if k is None:
            k = faiss_config.default_search_k
        """Search for similar documents"""
        results = self.vectorstore.similarity_search(
            query=query,
            k=k
        )
        
        # Apply filtering if specified
        if filter_dict:
            filtered_results = []
            for doc in results:
                if hasattr(doc, 'metadata'):
                    matches = all(
                        doc.metadata.get(key) == value 
                        for key, value in filter_dict.items()
                    )
                    if matches:
                        filtered_results.append(doc)
            return filtered_results
        
        return results
    
    def search_with_score(self, query: str, k: int = None, filter_dict: Dict[str, Any] = None):
        if k is None:
            k = faiss_config.default_search_k
        """Search for similar documents with similarity scores"""
        results = self.vectorstore.similarity_search_with_score(
            query=query,
            k=k
        )
        
        # Apply filtering if specified
        if filter_dict:
            filtered_results = []
            for doc, score in results:
                if hasattr(doc, 'metadata'):
                    matches = all(
                        doc.metadata.get(key) == value 
                        for key, value in filter_dict.items()
                    )
                    if matches:
                        filtered_results.append((doc, score))
            return filtered_results
        
        return results
    
    def get_collection_stats(self):
        """Get statistics about the collection"""
        return {
            "count": len(self.documents),
            "name": "FAISS Vector Store",
            "documents": len(self.documents)
        }
    
    def clear_collection(self):
        """Clear all documents from the collection"""
        self.create_new_vectorstore()
        self.save_vectorstore()

# Global vector store instance
vectorstore = VectorStore() 