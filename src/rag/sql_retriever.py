"""
SQL Retriever

Multi-modal retrieval with:
- Semantic similarity search
- Schema matching filter
- Complexity ranking
"""

from typing import Optional, Any
from dataclasses import dataclass

from src.rag.embeddings import EmbeddingModel, get_embedding_model
from src.rag.vector_store import FAISSVectorStore, get_vector_store


@dataclass
class SQLExample:
    """SQL example structure"""
    id: str
    natural_query: str
    sql: str
    tables: list[str]
    complexity: str  # simple, medium, complex
    tags: list[str]
    score: float = 0.0


class SQLRetriever:
    """Multi-modal SQL example retriever"""
    
    def __init__(
        self,
        embedding_model: Optional[EmbeddingModel] = None,
        vector_store: Optional[FAISSVectorStore] = None
    ):
        self.embedding_model = embedding_model or get_embedding_model()
        self.vector_store = vector_store
        self._initialized = False
    
    async def initialize(self):
        """Initialize vector store with correct dimension"""
        if self._initialized:
            return
        
        if self.vector_store is None:
            dimension = self.embedding_model.dimension
            self.vector_store = get_vector_store(dimension=dimension)
        
        self._initialized = True
    
    async def add_examples(self, examples: list[dict]) -> list[str]:
        """
        Add SQL examples to the store
        
        Args:
            examples: List of SQL example dicts with keys:
                - natural_query: Natural language query
                - sql: SQL statement
                - tables: List of table names used
                - complexity: simple/medium/complex
                - tags: List of tags
        
        Returns:
            List of added document IDs
        """
        await self.initialize()
        
        # Generate embeddings for natural queries
        queries = [ex["natural_query"] for ex in examples]
        embeddings = await self.embedding_model.embed(queries)
        
        # Add to vector store
        ids = self.vector_store.add(embeddings, examples)
        
        return ids
    
    async def retrieve(
        self,
        query: str,
        relevant_tables: Optional[list[str]] = None,
        top_k: int = 5,
        complexity_hint: Optional[str] = None
    ) -> list[SQLExample]:
        """
        Retrieve similar SQL examples
        
        Args:
            query: User's natural language query
            relevant_tables: Tables identified by schema retriever
            top_k: Number of results
            complexity_hint: Expected complexity level
            
        Returns:
            List of SQLExample objects sorted by relevance
        """
        await self.initialize()
        
        if self.vector_store.count == 0:
            return []
        
        # L1: Semantic search
        query_embedding = await self.embedding_model.embed(query)
        
        # L2: Schema matching filter
        def schema_filter(doc: dict) -> bool:
            if relevant_tables is None:
                return True
            doc_tables = set(doc.get("tables", []))
            query_tables = set(relevant_tables)
            # At least one table should match
            return len(doc_tables & query_tables) > 0
        
        # Search with larger k for filtering
        results = self.vector_store.search(
            query_embedding,
            top_k=top_k * 3,
            filter_fn=schema_filter
        )
        
        # L3: Complexity ranking
        if complexity_hint:
            results = self._rank_by_complexity(results, complexity_hint)
        
        # Convert to SQLExample objects
        examples = []
        for doc, score in results[:top_k]:
            example = SQLExample(
                id=doc.get("_id", ""),
                natural_query=doc.get("natural_query", ""),
                sql=doc.get("sql", ""),
                tables=doc.get("tables", []),
                complexity=doc.get("complexity", "medium"),
                tags=doc.get("tags", []),
                score=score
            )
            examples.append(example)
        
        return examples
    
    def _rank_by_complexity(
        self,
        results: list[tuple[dict, float]],
        target_complexity: str
    ) -> list[tuple[dict, float]]:
        """Re-rank results by complexity match"""
        complexity_order = {"simple": 0, "medium": 1, "complex": 2}
        target_level = complexity_order.get(target_complexity, 1)
        
        def complexity_score(item):
            doc, semantic_score = item
            doc_level = complexity_order.get(doc.get("complexity", "medium"), 1)
            # Penalize complexity mismatch
            complexity_penalty = abs(target_level - doc_level) * 0.1
            return semantic_score - complexity_penalty
        
        return sorted(results, key=complexity_score, reverse=True)
    
    def format_for_prompt(self, examples: list[SQLExample]) -> str:
        """Format examples for LLM prompt"""
        if not examples:
            return ""
        
        lines = ["## Similar SQL Examples\n"]
        
        for i, ex in enumerate(examples, 1):
            lines.append(f"### Example {i}")
            lines.append(f"**Query**: {ex.natural_query}")
            lines.append(f"**Tables**: {', '.join(ex.tables)}")
            lines.append(f"```sql\n{ex.sql}\n```")
            lines.append("")
        
        return "\n".join(lines)
    
    def save(self):
        """Save vector store to disk"""
        if self.vector_store:
            self.vector_store.save()
    
    @property
    def count(self) -> int:
        """Number of examples in store"""
        return self.vector_store.count if self.vector_store else 0


# Global singleton
_sql_retriever: Optional[SQLRetriever] = None


async def get_sql_retriever() -> SQLRetriever:
    """Get SQL retriever singleton"""
    global _sql_retriever
    if _sql_retriever is None:
        _sql_retriever = SQLRetriever()
        await _sql_retriever.initialize()
    return _sql_retriever
