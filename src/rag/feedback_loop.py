"""
Feedback Loop Module

Implements continuous learning by:
- Capturing successful SQL executions
- Adding them to the knowledge base
- Improving future retrievals
"""

from typing import Optional
from src.rag.data_loader import add_successful_sql
from src.agents.state import SQLAgentState


async def capture_success(state: SQLAgentState) -> bool:
    """
    Capture successful SQL execution and add to knowledge base
    
    Args:
        state: Agent state after successful execution
        
    Returns:
        True if successfully added
    """
    execution_result = state.get("execution_result", {})
    
    # Only capture successful executions
    if not execution_result.get("success", False):
        return False
    
    user_query = state.get("user_query", "")
    generated_sql = state.get("generated_sql", "")
    relevant_tables = state.get("relevant_tables", [])
    
    if not user_query or not generated_sql:
        return False
    
    # Estimate complexity based on SQL features
    complexity = estimate_complexity(generated_sql)
    
    try:
        doc_id = await add_successful_sql(
            natural_query=user_query,
            sql=generated_sql,
            tables=relevant_tables,
            complexity=complexity
        )
        return bool(doc_id)
    except Exception as e:
        print(f"Error capturing SQL: {e}")
        return False


def estimate_complexity(sql: str) -> str:
    """Estimate SQL complexity based on features"""
    sql_upper = sql.upper()
    
    score = 0
    
    # Check for complex features
    if "JOIN" in sql_upper:
        score += 1
    if "GROUP BY" in sql_upper:
        score += 1
    if "HAVING" in sql_upper:
        score += 1
    if "SUBQUERY" in sql_upper or "SELECT" in sql_upper[sql_upper.find("FROM"):]:
        score += 2
    if sql_upper.count("JOIN") > 1:
        score += 1
    if "UNION" in sql_upper:
        score += 2
    
    if score <= 1:
        return "simple"
    elif score <= 3:
        return "medium"
    else:
        return "complex"
