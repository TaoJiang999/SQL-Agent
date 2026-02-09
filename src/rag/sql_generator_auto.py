"""
SQL Example Auto-Generator

Generates SQL examples based on database schema using LLM
"""

from typing import Optional, Any
import json
from langchain_core.messages import HumanMessage

from src.config.llm import get_llm


GENERATION_PROMPT = """You are a SQL expert. Based on the following database schema, generate diverse SQL query examples.

## Database Schema

{schema}

## Requirements

Generate {count} SQL query examples covering:
1. Basic queries (SELECT, WHERE, ORDER BY, LIMIT)
2. Aggregation (COUNT, SUM, AVG, MAX, MIN, GROUP BY, HAVING)
3. JOIN operations (INNER, LEFT, RIGHT)
4. Subqueries (IN, EXISTS)
5. Complex combinations

For each example, provide:
- natural_query: Natural language description (in Chinese)
- sql: The SQL query
- tables: List of tables used
- complexity: simple/medium/complex
- tags: List of operation tags

## Output Format

Return a JSON array:
```json
[
  {{
    "natural_query": "查询所有价格大于100的商品",
    "sql": "SELECT * FROM products WHERE price > 100",
    "tables": ["products"],
    "complexity": "simple",
    "tags": ["select", "where", "comparison"]
  }}
]
```

Generate {count} diverse examples now:
"""


async def generate_sql_examples(
    schema_info: dict,
    count: int = 20
) -> list[dict]:
    """
    Generate SQL examples from schema using LLM
    
    Args:
        schema_info: Database schema information
        count: Number of examples to generate
        
    Returns:
        List of SQL example dicts
    """
    llm = get_llm()
    
    # Format schema for prompt
    schema_text = format_schema_for_generation(schema_info)
    
    prompt = GENERATION_PROMPT.format(
        schema=schema_text,
        count=count
    )
    
    try:
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        
        # Parse JSON response
        content = response.content
        
        # Extract JSON from markdown code block if present
        if "```json" in content:
            start = content.find("```json") + 7
            end = content.find("```", start)
            content = content[start:end].strip()
        elif "```" in content:
            start = content.find("```") + 3
            end = content.find("```", start)
            content = content[start:end].strip()
        
        examples = json.loads(content)
        
        # Validate examples
        validated = []
        for ex in examples:
            if validate_example(ex):
                validated.append(ex)
        
        return validated
        
    except Exception as e:
        print(f"Error generating SQL examples: {e}")
        return []


def format_schema_for_generation(schema_info: dict) -> str:
    """Format schema info for LLM prompt"""
    tables = schema_info.get("tables", {})
    
    lines = []
    for table_name, columns in tables.items():
        lines.append(f"### Table: {table_name}")
        for col in columns:
            col_name = col.get("name", col.get("column_name", ""))
            col_type = col.get("type", col.get("data_type", ""))
            is_pk = col.get("is_primary", col.get("column_key") == "PRI")
            pk_marker = " (PRIMARY KEY)" if is_pk else ""
            lines.append(f"  - {col_name}: {col_type}{pk_marker}")
        lines.append("")
    
    return "\n".join(lines)


def validate_example(example: dict) -> bool:
    """Validate SQL example structure"""
    required_fields = ["natural_query", "sql", "tables"]
    
    for field in required_fields:
        if field not in example or not example[field]:
            return False
    
    # Ensure tables is a list
    if not isinstance(example.get("tables"), list):
        return False
    
    # Set defaults for optional fields
    example.setdefault("complexity", "medium")
    example.setdefault("tags", [])
    
    return True


# Base examples for common patterns
BASE_EXAMPLES = [
    {
        "natural_query": "查询所有用户信息",
        "sql": "SELECT * FROM users",
        "tables": ["users"],
        "complexity": "simple",
        "tags": ["select", "basic"]
    },
    {
        "natural_query": "查询价格大于100的商品名称和价格",
        "sql": "SELECT name, price FROM products WHERE price > 100",
        "tables": ["products"],
        "complexity": "simple",
        "tags": ["select", "where", "comparison"]
    },
    {
        "natural_query": "统计每个分类的商品数量",
        "sql": "SELECT c.name, COUNT(p.id) as product_count FROM categories c LEFT JOIN products p ON c.id = p.category_id GROUP BY c.id",
        "tables": ["categories", "products"],
        "complexity": "medium",
        "tags": ["join", "group_by", "count"]
    },
    {
        "natural_query": "查询销量最高的10个商品",
        "sql": "SELECT p.name, SUM(oi.quantity) as total_sold FROM products p JOIN order_items oi ON p.id = oi.product_id GROUP BY p.id ORDER BY total_sold DESC LIMIT 10",
        "tables": ["products", "order_items"],
        "complexity": "medium",
        "tags": ["join", "group_by", "order_by", "limit", "sum"]
    },
    {
        "natural_query": "查询每个用户的订单总金额",
        "sql": "SELECT u.username, SUM(o.total_amount) as total_spent FROM users u JOIN orders o ON u.id = o.user_id GROUP BY u.id ORDER BY total_spent DESC",
        "tables": ["users", "orders"],
        "complexity": "medium",
        "tags": ["join", "group_by", "order_by", "sum"]
    },
    {
        "natural_query": "查询没有下过订单的用户",
        "sql": "SELECT * FROM users WHERE id NOT IN (SELECT DISTINCT user_id FROM orders)",
        "tables": ["users", "orders"],
        "complexity": "complex",
        "tags": ["subquery", "not_in"]
    },
    {
        "natural_query": "查询评分最高的5个商品及其评分",
        "sql": "SELECT p.name, AVG(r.rating) as avg_rating, COUNT(r.id) as review_count FROM products p JOIN reviews r ON p.id = r.product_id GROUP BY p.id HAVING COUNT(r.id) >= 3 ORDER BY avg_rating DESC LIMIT 5",
        "tables": ["products", "reviews"],
        "complexity": "complex",
        "tags": ["join", "group_by", "having", "avg", "order_by", "limit"]
    },
    {
        "natural_query": "查询2024年每月的销售额",
        "sql": "SELECT DATE_FORMAT(created_at, '%Y-%m') as month, SUM(total_amount) as monthly_sales FROM orders WHERE YEAR(created_at) = 2024 GROUP BY month ORDER BY month",
        "tables": ["orders"],
        "complexity": "medium",
        "tags": ["date_format", "group_by", "sum", "where"]
    },
    {
        "natural_query": "查询购买了特定商品的所有用户",
        "sql": "SELECT DISTINCT u.* FROM users u JOIN orders o ON u.id = o.user_id JOIN order_items oi ON o.id = oi.order_id WHERE oi.product_id = ?",
        "tables": ["users", "orders", "order_items"],
        "complexity": "complex",
        "tags": ["join", "distinct", "parameter"]
    },
    {
        "natural_query": "统计各状态的订单数量",
        "sql": "SELECT status, COUNT(*) as order_count FROM orders GROUP BY status",
        "tables": ["orders"],
        "complexity": "simple",
        "tags": ["group_by", "count"]
    }
]


def get_base_examples() -> list[dict]:
    """Get base SQL examples"""
    return BASE_EXAMPLES.copy()
