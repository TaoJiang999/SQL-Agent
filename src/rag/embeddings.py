"""
Embedding Module

Supports:
- Local models (sentence-transformers)
- API-based models (OpenAI)
"""

from typing import Optional, Union
import numpy as np
from abc import ABC, abstractmethod

from src.config.settings import get_settings


class BaseEmbedding(ABC):
    """Base embedding interface"""
    
    @abstractmethod
    async def embed_text(self, text: str) -> np.ndarray:
        """Embed single text"""
        pass
    
    @abstractmethod
    async def embed_texts(self, texts: list[str]) -> np.ndarray:
        """Embed multiple texts"""
        pass
    
    @property
    @abstractmethod
    def dimension(self) -> int:
        """Embedding dimension"""
        pass


class SentenceTransformerEmbedding(BaseEmbedding):
    """Local embedding using sentence-transformers"""
    
    def __init__(self, model_name: str = "BAAI/bge-small-zh-v1.5"):
        """
        Args:
            model_name: HuggingFace model name
                - BAAI/bge-small-zh-v1.5 (Chinese, 512 dim)
                - BAAI/bge-base-zh-v1.5 (Chinese, 768 dim)
                - sentence-transformers/all-MiniLM-L6-v2 (English, 384 dim)
        """
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
            self._dimension = self.model.get_sentence_embedding_dimension()
        except ImportError:
            raise ImportError("Please install sentence-transformers: pip install sentence-transformers")
    
    async def embed_text(self, text: str) -> np.ndarray:
        """Embed single text"""
        embedding = self.model.encode(text, normalize_embeddings=True)
        return np.array(embedding, dtype=np.float32)
    
    async def embed_texts(self, texts: list[str]) -> np.ndarray:
        """Embed multiple texts with batching"""
        embeddings = self.model.encode(
            texts, 
            normalize_embeddings=True,
            batch_size=32,
            show_progress_bar=len(texts) > 100
        )
        return np.array(embeddings, dtype=np.float32)
    
    @property
    def dimension(self) -> int:
        return self._dimension


class OpenAIEmbedding(BaseEmbedding):
    """OpenAI API embedding"""
    
    def __init__(self, model_name: str = "text-embedding-3-small"):
        self.model_name = model_name
        self._dimension = 1536 if "3-small" in model_name else 3072
        
        try:
            from openai import AsyncOpenAI
            settings = get_settings()
            self.client = AsyncOpenAI(
                api_key=settings.model_api_key,
                base_url=settings.model_base_url
            )
        except ImportError:
            raise ImportError("Please install openai: pip install openai")
    
    async def embed_text(self, text: str) -> np.ndarray:
        """Embed single text"""
        response = await self.client.embeddings.create(
            model=self.model_name,
            input=text
        )
        return np.array(response.data[0].embedding, dtype=np.float32)
    
    async def embed_texts(self, texts: list[str]) -> np.ndarray:
        """Embed multiple texts"""
        # OpenAI supports batch embedding
        response = await self.client.embeddings.create(
            model=self.model_name,
            input=texts
        )
        embeddings = [item.embedding for item in response.data]
        return np.array(embeddings, dtype=np.float32)
    
    @property
    def dimension(self) -> int:
        return self._dimension


class EmbeddingModel:
    """Unified embedding model wrapper"""
    
    def __init__(
        self, 
        provider: str = "local",
        model_name: Optional[str] = None
    ):
        """
        Args:
            provider: "local" or "openai"
            model_name: Model name (optional, uses default if not specified)
        """
        self.provider = provider
        
        if provider == "local":
            model_name = model_name or "BAAI/bge-small-zh-v1.5"
            self._model = SentenceTransformerEmbedding(model_name)
        elif provider == "openai":
            model_name = model_name or "text-embedding-3-small"
            self._model = OpenAIEmbedding(model_name)
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    async def embed(self, text: Union[str, list[str]]) -> np.ndarray:
        """Embed text or list of texts"""
        if isinstance(text, str):
            return await self._model.embed_text(text)
        return await self._model.embed_texts(text)
    
    @property
    def dimension(self) -> int:
        return self._model.dimension


# Global singleton
_embedding_model: Optional[EmbeddingModel] = None


def get_embedding_model(
    provider: str = "local",
    model_name: Optional[str] = None
) -> EmbeddingModel:
    """Get embedding model singleton"""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = EmbeddingModel(provider, model_name)
    return _embedding_model
