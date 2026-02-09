"""
FAISS Vector Store

GPU-accelerated vector storage and retrieval
"""

from typing import Optional, Any
from pathlib import Path
import numpy as np
import json


class FAISSVectorStore:
    """FAISS-based vector store with GPU support"""
    
    def __init__(
        self,
        dimension: int,
        index_path: Optional[str] = None,
        use_gpu: bool = True
    ):
        """
        Args:
            dimension: Vector dimension
            index_path: Path to save/load index
            use_gpu: Whether to use GPU acceleration
        """
        try:
            import faiss
            self.faiss = faiss
        except ImportError:
            raise ImportError("Please install faiss: pip install faiss-gpu or faiss-cpu")
        
        self.dimension = dimension
        self.index_path = Path(index_path) if index_path else None
        self.use_gpu = use_gpu
        
        # Initialize index
        self._index = None
        self._gpu_index = None
        self._documents: list[dict] = []
        self._id_map: dict[str, int] = {}
        
        # Try to load existing index
        if self.index_path and self.index_path.exists():
            self.load()
        else:
            self._create_index()
    
    def _create_index(self):
        """Create new FAISS index"""
        # Use Inner Product for normalized vectors (equivalent to cosine similarity)
        self._index = self.faiss.IndexFlatIP(self.dimension)
        
        # Move to GPU if available and requested
        if self.use_gpu:
            try:
                res = self.faiss.StandardGpuResources()
                self._gpu_index = self.faiss.index_cpu_to_gpu(res, 0, self._index)
            except Exception:
                # Fall back to CPU if GPU not available
                self._gpu_index = None
    
    @property
    def index(self):
        """Get active index (GPU or CPU)"""
        return self._gpu_index if self._gpu_index else self._index
    
    def add(
        self,
        embeddings: np.ndarray,
        documents: list[dict],
        ids: Optional[list[str]] = None
    ) -> list[str]:
        """
        Add vectors and documents to the store
        
        Args:
            embeddings: Vectors to add (n, dimension)
            documents: Document metadata list
            ids: Optional document IDs
            
        Returns:
            List of document IDs
        """
        if len(embeddings) != len(documents):
            raise ValueError("Embeddings and documents must have same length")
        
        # Ensure embeddings are float32 and contiguous
        embeddings = np.ascontiguousarray(embeddings, dtype=np.float32)
        
        # Generate IDs if not provided
        if ids is None:
            start_id = len(self._documents)
            ids = [f"doc_{start_id + i}" for i in range(len(documents))]
        
        # Add to index
        start_idx = self._index.ntotal
        self._index.add(embeddings)
        
        # Update GPU index if using GPU
        if self._gpu_index:
            self._gpu_index = self.faiss.index_cpu_to_gpu(
                self.faiss.StandardGpuResources(), 0, self._index
            )
        
        # Store documents and ID mapping
        for i, (doc_id, doc) in enumerate(zip(ids, documents)):
            self._id_map[doc_id] = start_idx + i
            doc["_id"] = doc_id
            self._documents.append(doc)
        
        return ids
    
    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        filter_fn: Optional[callable] = None
    ) -> list[tuple[dict, float]]:
        """
        Search for similar vectors
        
        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            filter_fn: Optional function to filter results
            
        Returns:
            List of (document, score) tuples
        """
        if self.index.ntotal == 0:
            return []
        
        # Ensure query is 2D
        query = np.ascontiguousarray(
            query_embedding.reshape(1, -1), 
            dtype=np.float32
        )
        
        # Search with more results if filtering
        search_k = top_k * 3 if filter_fn else top_k
        search_k = min(search_k, self.index.ntotal)
        
        scores, indices = self.index.search(query, search_k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self._documents):
                continue
            
            doc = self._documents[idx]
            
            # Apply filter if provided
            if filter_fn and not filter_fn(doc):
                continue
            
            results.append((doc, float(score)))
            
            if len(results) >= top_k:
                break
        
        return results
    
    def save(self, path: Optional[str] = None):
        """Save index and documents to disk"""
        save_path = Path(path) if path else self.index_path
        if not save_path:
            raise ValueError("No save path specified")
        
        save_path.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index (CPU version)
        index_file = save_path / "index.faiss"
        self.faiss.write_index(self._index, str(index_file))
        
        # Save documents and ID map
        meta_file = save_path / "metadata.json"
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump({
                "documents": self._documents,
                "id_map": self._id_map,
                "dimension": self.dimension
            }, f, ensure_ascii=False, indent=2)
    
    def load(self, path: Optional[str] = None):
        """Load index and documents from disk"""
        load_path = Path(path) if path else self.index_path
        if not load_path:
            raise ValueError("No load path specified")
        
        index_file = load_path / "index.faiss"
        meta_file = load_path / "metadata.json"
        
        if not index_file.exists() or not meta_file.exists():
            self._create_index()
            return
        
        # Load FAISS index
        self._index = self.faiss.read_index(str(index_file))
        
        # Move to GPU if available
        if self.use_gpu:
            try:
                res = self.faiss.StandardGpuResources()
                self._gpu_index = self.faiss.index_cpu_to_gpu(res, 0, self._index)
            except Exception:
                self._gpu_index = None
        
        # Load metadata
        with open(meta_file, "r", encoding="utf-8") as f:
            meta = json.load(f)
            self._documents = meta["documents"]
            self._id_map = meta["id_map"]
    
    def clear(self):
        """Clear all data"""
        self._create_index()
        self._documents = []
        self._id_map = {}
    
    @property
    def count(self) -> int:
        """Number of vectors in the store"""
        return self._index.ntotal


# Global singleton
_vector_store: Optional[FAISSVectorStore] = None


def get_vector_store(
    dimension: int = 512,
    index_path: str = "data/sql_examples/faiss_index",
    use_gpu: bool = True
) -> FAISSVectorStore:
    """Get vector store singleton"""
    global _vector_store
    if _vector_store is None:
        _vector_store = FAISSVectorStore(
            dimension=dimension,
            index_path=index_path,
            use_gpu=use_gpu
        )
    return _vector_store
