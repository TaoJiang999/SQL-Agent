"""
SQL Executor - SQL Validation and Execution Node

Responsibilities:
- Execute SQL safely in sandbox environment
- Capture execution errors and traceback
- Return execution results with formatted display
"""

from typing import Any, Optional
import asyncio
import aiomysql
from langchain_core.messages import AIMessage

from src.config.settings import get_settings
from src.agents.state import SQLAgentState


class SQLExecutor:
    """SQL Executor"""
    
    def __init__(self):
        self.settings = get_settings()
        self._pool: Optional[aiomysql.Pool] = None
    
    async def get_pool(self) -> aiomysql.Pool:
        """Get database connection pool"""
        if self._pool is None:
            self._pool = await aiomysql.create_pool(
                host=self.settings.sandbox_db_host,
                port=self.settings.sandbox_db_port,
                user=self.settings.sandbox_db_user,
                password=self.settings.sandbox_db_password,
                db=self.settings.sandbox_db_name,
                charset='utf8mb4',
                autocommit=True,
                minsize=1,
                maxsize=5
            )
        return self._pool
    
    async def execute_sql(self, sql: str, timeout: int = 30) -> dict[str, Any]:
        """Execute SQL statement"""
        pool = await self.get_pool()
        
        try:
            async with pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cur:
                    await asyncio.wait_for(
                        cur.execute(sql),
                        timeout=timeout
                    )
                    
                    if sql.strip().upper().startswith("SELECT"):
                        rows = await cur.fetchall()
                        return {
                            "success": True,
                            "data": rows,
                            "row_count": len(rows),
                            "columns": [desc[0] for desc in cur.description] if cur.description else []
                        }
                    else:
                        return {
                            "success": True,
                            "affected_rows": cur.rowcount,
                            "message": f"Executed successfully, affected {cur.rowcount} rows"
                        }
                        
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "Query timeout",
                "error_type": "TimeoutError"
            }
        except aiomysql.Error as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": e.args[0] if e.args else None,
                "error_type": type(e).__name__
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    async def validate_sql(self, sql: str) -> dict[str, Any]:
        """Validate SQL syntax using EXPLAIN"""
        if not sql.strip().upper().startswith("SELECT"):
            return {
                "valid": False,
                "error": "Only SELECT queries are supported"
            }
        
        pool = await self.get_pool()
        
        try:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(f"EXPLAIN {sql}")
                    await cur.fetchall()
                    return {"valid": True}
        except aiomysql.Error as e:
            return {
                "valid": False,
                "error": str(e)
            }
    
    async def close(self):
        """Close connection pool"""
        if self._pool:
            self._pool.close()
            await self._pool.wait_closed()
            self._pool = None


# Global instance
_executor: Optional[SQLExecutor] = None


def get_sql_executor() -> SQLExecutor:
    """Get SQL executor singleton"""
    global _executor
    if _executor is None:
        _executor = SQLExecutor()
    return _executor


def format_result_as_table(columns: list, data: list, max_rows: int = 10) -> str:
    """Format query result as markdown table"""
    if not data or not columns:
        return "No data returned."
    
    # Limit rows for display
    display_data = data[:max_rows]
    
    # Build markdown table
    lines = []
    
    # Header
    lines.append("| " + " | ".join(str(col) for col in columns) + " |")
    lines.append("|" + "|".join("---" for _ in columns) + "|")
    
    # Rows
    for row in display_data:
        row_values = []
        for col in columns:
            val = row.get(col, "")
            # Truncate long values
            val_str = str(val) if val is not None else "NULL"
            if len(val_str) > 50:
                val_str = val_str[:47] + "..."
            row_values.append(val_str)
        lines.append("| " + " | ".join(row_values) + " |")
    
    if len(data) > max_rows:
        lines.append(f"\n... and {len(data) - max_rows} more rows")
    
    return "\n".join(lines)


async def sql_executor_node(state: SQLAgentState) -> SQLAgentState:
    """SQL execution node"""
    executor = get_sql_executor()
    
    generated_sql = state.get("generated_sql", "")
    intent = state.get("intent", "")
    messages = state.get("messages", [])
    
    # For sql_to_text mode, no execution needed
    if intent == "sql_to_text":
        explanation = state.get("sql_explanation", "")
        return {
            **state,
            "current_agent": "sql_executor",
            "execution_result": {
                "success": True,
                "message": "SQL explanation completed",
                "explanation": explanation
            },
            "messages": [
                *messages,
                AIMessage(content=f"**SQL Explanation:**\n\n{explanation}")
            ]
        }
    
    if not generated_sql:
        return {
            **state,
            "current_agent": "sql_executor",
            "execution_error": "No SQL to execute",
            "execution_result": {"success": False},
            "messages": [
                *messages,
                AIMessage(content="Error: No SQL statement to execute.")
            ]
        }
    
    # Validate SQL
    validation = await executor.validate_sql(generated_sql)
    if not validation.get("valid", False):
        return {
            **state,
            "current_agent": "sql_executor",
            "execution_error": validation.get("error", "SQL validation failed"),
            "execution_result": {"success": False}
        }
    
    # Execute SQL
    result = await executor.execute_sql(generated_sql)
    
    if result.get("success", False):
        data = result.get("data", [])
        row_count = result.get("row_count", 0)
        columns = result.get("columns", [])
        
        # Format result as table for display
        table_display = format_result_as_table(columns, data)
        
        # Build response message
        response_parts = [
            f"**Generated SQL:**\n```sql\n{generated_sql}\n```",
            f"\n**Query Result:** {row_count} rows returned\n",
            table_display
        ]
        response_message = "\n".join(response_parts)
        
        return {
            **state,
            "current_agent": "sql_executor",
            "execution_result": {
                "success": True,
                "data": data[:100],
                "total_rows": row_count,
                "columns": columns,
                "truncated": len(data) > 100
            },
            "execution_error": None,
            "messages": [
                *messages,
                AIMessage(content=response_message)
            ]
        }
    else:
        error_msg = result.get("error", "Unknown error")
        return {
            **state,
            "current_agent": "sql_executor",
            "execution_result": {"success": False},
            "execution_error": error_msg,
            "messages": [
                *messages,
                AIMessage(content=f"**SQL Execution Failed:**\n```sql\n{generated_sql}\n```\n\n**Error:** {error_msg}")
            ]
        }


def should_retry(state: SQLAgentState) -> str:
    """Conditional routing: determine if retry is needed"""
    execution_error = state.get("execution_error")
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 3)
    
    if not execution_error:
        return "end"
    
    if retry_count >= max_retries:
        return "end"
    
    return "retry"
