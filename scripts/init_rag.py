"""
RAG Initialization and Testing Script

Usage:
    python scripts/init_rag.py init    # Initialize vector store with examples
    python scripts/init_rag.py test    # Test retrieval
    python scripts/init_rag.py status  # Check status
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


async def init_command():
    """Initialize vector store with SQL examples"""
    from src.rag.data_loader import initialize_vector_store
    
    print("=" * 60)
    print("🚀 Initializing RAG Vector Store")
    print("=" * 60)
    
    count = await initialize_vector_store(
        include_base=True,
        include_generated=False  # Don't auto-generate, use existing examples
    )
    
    print(f"\n✅ Initialized with {count} SQL examples")
    print("=" * 60)


async def test_command():
    """Test SQL retrieval"""
    from src.rag.sql_retriever import get_sql_retriever
    
    print("=" * 60)
    print("🔍 Testing SQL Retrieval")
    print("=" * 60)
    
    retriever = await get_sql_retriever()
    
    if retriever.count == 0:
        print("❌ Vector store is empty. Run 'init' first.")
        return
    
    print(f"📊 Vector store contains {retriever.count} examples\n")
    
    # Test queries
    test_queries = [
        ("查询所有商品", ["products"]),
        ("查询销量最高的商品", ["products", "order_items"]),
        ("统计每个分类的商品数量", ["products", "categories"]),
        ("查询用户的订单信息", ["users", "orders"]),
        ("查询没有下单的用户", ["users", "orders"]),
    ]
    
    for query, tables in test_queries:
        print(f"\n{'─' * 50}")
        print(f"📥 Query: {query}")
        print(f"📋 Tables: {tables}")
        print(f"{'─' * 50}")
        
        examples = await retriever.retrieve(
            query=query,
            relevant_tables=tables,
            top_k=3
        )
        
        if not examples:
            print("⚠️ No similar examples found")
            continue
        
        for i, ex in enumerate(examples, 1):
            print(f"\n  🔹 Result {i} (Score: {ex.score:.4f})")
            print(f"     Query: {ex.natural_query}")
            print(f"     Tables: {ex.tables}")
            print(f"     Complexity: {ex.complexity}")
            print(f"     SQL: {ex.sql[:80]}{'...' if len(ex.sql) > 80 else ''}")
    
    print("\n" + "=" * 60)
    print("✅ Test completed")
    print("=" * 60)


async def status_command():
    """Check vector store status"""
    from src.rag.sql_retriever import get_sql_retriever
    from src.rag.embeddings import get_embedding_model
    
    print("=" * 60)
    print("📊 RAG Status")
    print("=" * 60)
    
    # Check embedding model
    try:
        model = get_embedding_model()
        print(f"✅ Embedding Model: dimension={model.dimension}")
    except Exception as e:
        print(f"❌ Embedding Model Error: {e}")
    
    # Check vector store
    try:
        retriever = await get_sql_retriever()
        print(f"✅ Vector Store: {retriever.count} examples")
    except Exception as e:
        print(f"❌ Vector Store Error: {e}")
    
    # Check data files
    data_dir = Path("data/sql_examples")
    if data_dir.exists():
        json_files = list(data_dir.glob("*.json"))
        print(f"✅ Data Files: {len(json_files)} JSON files")
        for f in json_files:
            print(f"   - {f.name}")
    else:
        print("⚠️ Data directory not found")
    
    print("=" * 60)


async def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    command = sys.argv[1].lower()
    
    if command == "init":
        await init_command()
    elif command == "test":
        await test_command()
    elif command == "status":
        await status_command()
    else:
        print(f"❌ Unknown command: {command}")
        print(__doc__)


if __name__ == "__main__":
    asyncio.run(main())
