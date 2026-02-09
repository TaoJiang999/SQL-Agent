"""
Data Loader

Initialize and manage SQL examples in vector store
"""

import json
from pathlib import Path
from typing import Optional
import asyncio

from src.rag.embeddings import get_embedding_model
from src.rag.vector_store import get_vector_store
from src.rag.sql_retriever import SQLRetriever, get_sql_retriever
from src.rag.sql_generator_auto import generate_sql_examples, get_base_examples


DATA_DIR = Path("data/sql_examples")


async def initialize_vector_store(
    include_base: bool = True,
    include_generated: bool = True,
    schema_info: Optional[dict] = None,
    generate_count: int = 30
) -> int:
    """
    Initialize vector store with SQL examples
    
    Args:
        include_base: Include hand-crafted base examples
        include_generated: Include auto-generated examples
        schema_info: Database schema for generation
        generate_count: Number of examples to generate
        
    Returns:
        Total number of examples loaded
    """
    retriever = await get_sql_retriever()
    
    all_examples = []
    
    # Load base examples
    if include_base:
        base_examples = get_base_examples()
        all_examples.extend(base_examples)
        print(f"Loaded {len(base_examples)} base examples")
    
    # Load from JSON files
    json_examples = load_examples_from_files()
    all_examples.extend(json_examples)
    if json_examples:
        print(f"Loaded {len(json_examples)} examples from files")
    
    # Generate new examples if schema provided
    if include_generated and schema_info:
        generated = await generate_sql_examples(schema_info, generate_count)
        all_examples.extend(generated)
        print(f"Generated {len(generated)} new examples")
        
        # Save generated examples
        save_examples_to_file(generated, "generated_examples.json")
    
    # Add all to vector store
    if all_examples:
        ids = await retriever.add_examples(all_examples)
        print(f"Added {len(ids)} examples to vector store")
        
        # Save index
        retriever.save()
    
    return len(all_examples)


def load_examples_from_files() -> list[dict]:
    """Load examples from JSON files in data directory"""
    examples = []
    
    if not DATA_DIR.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        return examples
    
    for json_file in DATA_DIR.glob("*.json"):
        if json_file.name.startswith("faiss"):
            continue
        
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    examples.extend(data)
                else:
                    examples.append(data)
        except Exception as e:
            print(f"Error loading {json_file}: {e}")
    
    return examples


def save_examples_to_file(examples: list[dict], filename: str):
    """Save examples to JSON file"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    filepath = DATA_DIR / filename
    
    # Merge with existing if file exists
    existing = []
    if filepath.exists():
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except Exception:
            pass
    
    # Deduplicate by SQL
    existing_sqls = {ex.get("sql") for ex in existing}
    new_examples = [ex for ex in examples if ex.get("sql") not in existing_sqls]
    
    all_examples = existing + new_examples
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(all_examples, f, ensure_ascii=False, indent=2)
    
    print(f"Saved {len(new_examples)} new examples to {filepath}")


async def add_successful_sql(
    natural_query: str,
    sql: str,
    tables: list[str],
    complexity: str = "medium"
) -> str:
    """
    Add successfully executed SQL to the knowledge base (Feedback Loop)
    
    Args:
        natural_query: Original user query
        sql: Executed SQL
        tables: Tables used
        complexity: Estimated complexity
        
    Returns:
        Document ID
    """
    retriever = await get_sql_retriever()
    
    example = {
        "natural_query": natural_query,
        "sql": sql,
        "tables": tables,
        "complexity": complexity,
        "tags": ["learned"],
        "source": "feedback_loop"
    }
    
    # Add to vector store
    ids = await retriever.add_examples([example])
    
    # Persist to file
    save_examples_to_file([example], "learned_examples.json")
    
    # Save index
    retriever.save()
    
    return ids[0] if ids else ""


# CLI interface
if __name__ == "__main__":
    import sys
    
    async def main():
        if len(sys.argv) < 2:
            print("Usage: python -m src.rag.data_loader [init|status]")
            return
        
        command = sys.argv[1]
        
        if command == "init":
            count = await initialize_vector_store(include_generated=False)
            print(f"Initialized with {count} examples")
        
        elif command == "status":
            retriever = await get_sql_retriever()
            print(f"Vector store contains {retriever.count} examples")
        
        else:
            print(f"Unknown command: {command}")
    
    asyncio.run(main())
