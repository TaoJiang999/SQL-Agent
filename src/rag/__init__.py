"""
RAG Module for SQL Agent

Contains:
- Embedding models
- FAISS vector store
- SQL retriever
- Data loaders
- Feedback loop
"""

from src.rag.embeddings import EmbeddingModel, get_embedding_model
from src.rag.vector_store import FAISSVectorStore, get_vector_store
from src.rag.sql_retriever import SQLRetriever, get_sql_retriever
from src.rag.sql_generator_auto import generate_sql_examples, get_base_examples
from src.rag.data_loader import initialize_vector_store, add_successful_sql
from src.rag.feedback_loop import capture_success

__all__ = [
    "EmbeddingModel",
    "get_embedding_model",
    "FAISSVectorStore",
    "get_vector_store",
    "SQLRetriever",
    "get_sql_retriever",
    "generate_sql_examples",
    "get_base_examples",
    "initialize_vector_store",
    "add_successful_sql",
    "capture_success"
]
