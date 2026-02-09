"""
SQL Generator - SQL Generation/Translation/Debug Node with RAG Enhancement

Responsibilities:
- text_to_sql: Generate SQL from schema and user query with RAG examples
- sql_to_text: Explain SQL statement meaning
- debug: Fix SQL based on error messages
"""

from typing import Any
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from src.config.llm import get_llm
from src.agents.state import SQLAgentState


# Configuration
MAX_RETRY_COUNT = 3  # Maximum SQL fix attempts


# Text-to-SQL prompt with RAG examples
TEXT_TO_SQL_PROMPT = """You are a professional SQL expert. Generate correct MySQL SQL statements based on user requirements and database schema.

## Database Schema

{schema}

{rag_examples}

## User Request

{user_query}

## Requirements

1. Only generate SELECT queries, no INSERT/UPDATE/DELETE
2. Use correct table and column names
3. Consider JOIN relationships and foreign key constraints
4. Add appropriate WHERE conditions and ORDER BY
5. Return ONLY the SQL statement, no other explanation

## SQL Statement
"""

# SQL-to-Text prompt
SQL_TO_TEXT_PROMPT = """You are a SQL explanation expert. Explain this SQL statement in simple terms.

## Database Schema

{schema}

## SQL Statement

{sql}

## Explanation Requirements

1. State the purpose of the query
2. Explain the tables and columns involved
3. Describe filter conditions and sorting
4. Use business language to describe results

Please respond in the same language as the user's query.

## Explanation
"""

# Debug prompt
DEBUG_SQL_PROMPT = """You are a SQL debugging expert. Fix the SQL statement based on the error message.

## Database Schema

{schema}

## Original SQL

{sql}

## Error Message

{error}

## Fix Requirements

1. Analyze the error cause
2. Fix the SQL statement
3. Return ONLY the fixed SQL statement

## Fixed SQL
"""


async def sql_generator_node(state: SQLAgentState) -> SQLAgentState:
    """
    SQL generation node with RAG enhancement
    
    Executes different generation tasks based on intent type
    
    Args:
        state: Current state
        
    Returns:
        Updated state
    """
    llm = get_llm()
    intent = state.get("intent", "unknown")
    user_query = state.get("user_query", "")
    schema_info = state.get("schema_info", {})
    formatted_schema = schema_info.get("formatted", "") if schema_info else ""
    relevant_tables = state.get("relevant_tables", [])
    
    # Get existing SQL (for debug mode)
    existing_sql = state.get("generated_sql", "")
    execution_error = state.get("execution_error", "")
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", MAX_RETRY_COUNT)
    messages = state.get("messages", [])
    
    print(f"[sql_generator] intent={intent}, retry_count={retry_count}/{max_retries}, has_error={bool(execution_error)}")
    
    try:
        # If there's an execution error, go to debug/fix mode first
        if execution_error and existing_sql:
            # Check if we've exceeded max retries
            if retry_count >= max_retries:
                print(f"[sql_generator] Max retries ({max_retries}) reached, giving up")
                error_msg = f"SQL generation failed after {retry_count} attempts. Last error: {execution_error}"
                return {
                    **state,
                    "current_agent": "sql_generator",
                    "error": error_msg,
                    "messages": [
                        *messages,
                        AIMessage(content=f"抱歉，SQL生成失败。尝试了{retry_count}次仍未成功。\n\n**最后的错误:** {execution_error}")
                    ]
                }
            
            print(f"[sql_generator] Retry {retry_count + 1}/{max_retries}: Fixing SQL based on error")
            
            # Build context-aware fix prompt with error history
            prompt = DEBUG_SQL_PROMPT.format(
                schema=formatted_schema,
                sql=existing_sql,
                error=execution_error
            )
            response = await llm.ainvoke([HumanMessage(content=prompt)])
            fixed_sql = clean_sql(response.content.strip())
            
            return {
                **state,
                "generated_sql": fixed_sql.strip(),
                "execution_error": None,  # Clear error after fix
                "retry_count": retry_count + 1,
                "current_agent": "sql_generator",
            }
        
        elif intent == "text_to_sql":
            # Get RAG examples
            rag_examples_text = await get_rag_examples(user_query, relevant_tables)
            
            # Natural language to SQL
            prompt = TEXT_TO_SQL_PROMPT.format(
                schema=formatted_schema,
                rag_examples=rag_examples_text,
                user_query=user_query
            )
            response = await llm.ainvoke([HumanMessage(content=prompt)])
            generated_sql = response.content.strip()
            
            # Clean SQL (remove markdown code block markers)
            generated_sql = clean_sql(generated_sql)
            
            return {
                **state,
                "generated_sql": generated_sql.strip(),
                "current_agent": "sql_generator",
            }
            
        elif intent == "sql_to_text":
            # SQL to natural language
            sql_to_explain = user_query
            if "SELECT" in user_query.upper():
                import re
                match = re.search(r'(SELECT.+?)(?:$|\n\n)', user_query, re.IGNORECASE | re.DOTALL)
                if match:
                    sql_to_explain = match.group(1)
            
            prompt = SQL_TO_TEXT_PROMPT.format(
                schema=formatted_schema,
                sql=sql_to_explain
            )
            response = await llm.ainvoke([HumanMessage(content=prompt)])
            
            return {
                **state,
                "generated_sql": sql_to_explain,
                "sql_explanation": response.content.strip(),
                "current_agent": "sql_generator",
            }
            
        elif intent == "debug" or execution_error:
            # Debug/fix mode
            sql_to_fix = existing_sql or user_query
            error_msg = execution_error or "Unknown error"
            
            prompt = DEBUG_SQL_PROMPT.format(
                schema=formatted_schema,
                sql=sql_to_fix,
                error=error_msg
            )
            response = await llm.ainvoke([HumanMessage(content=prompt)])
            fixed_sql = clean_sql(response.content.strip())
            
            return {
                **state,
                "generated_sql": fixed_sql.strip(),
                "execution_error": None,
                "retry_count": retry_count + 1,
                "current_agent": "sql_generator",
            }
            
        else:
            return {
                **state,
                "current_agent": "sql_generator",
                "error": f"Unknown intent type: {intent}"
            }
            
    except Exception as e:
        return {
            **state,
            "current_agent": "sql_generator",
            "error": f"SQL generation failed: {str(e)}"
        }


async def get_rag_examples(
    query: str,
    relevant_tables: list[str],
    top_k: int = 3
) -> str:
    """
    Retrieve similar SQL examples using RAG
    
    Args:
        query: User's natural language query
        relevant_tables: Tables identified by schema retriever
        top_k: Number of examples to retrieve
        
    Returns:
        Formatted examples text for prompt
    """
    import asyncio
    
    try:
        # Run RAG retrieval in a separate thread to avoid blocking
        result = await asyncio.to_thread(
            _sync_rag_retrieve,
            query,
            relevant_tables,
            top_k
        )
        return result
        
    except Exception as e:
        # RAG is optional, don't fail if unavailable
        print(f"RAG retrieval failed: {e}")
        return ""


def _sync_rag_retrieve(query: str, relevant_tables: list[str], top_k: int) -> str:
    """Synchronous wrapper for RAG retrieval"""
    import asyncio
    
    async def _retrieve():
        from src.rag.sql_retriever import get_sql_retriever
        
        retriever = await get_sql_retriever()
        
        if retriever.count == 0:
            return ""
        
        examples = await retriever.retrieve(
            query=query,
            relevant_tables=relevant_tables,
            top_k=top_k
        )
        
        if not examples:
            return ""
        
        return retriever.format_for_prompt(examples)
    
    # Run in a new event loop in the thread
    return asyncio.run(_retrieve())


def clean_sql(sql: str) -> str:
    """Clean SQL by removing markdown code block markers"""
    if sql.startswith("```"):
        lines = sql.split("\n")
        # Remove first line (```sql or ```)
        lines = lines[1:]
        # Remove last line if it's just ```
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        sql = "\n".join(lines)
    return sql.strip()
