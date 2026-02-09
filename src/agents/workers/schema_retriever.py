"""
Schema Retriever - 数据库元数据检索节点

负责：
- 连接数据库获取表结构信息
- 识别与用户查询相关的表
- 提供schema上下文给SQL生成器
"""

import asyncio
from typing import Any, Optional
import aiomysql
from langchain_core.messages import AIMessage, HumanMessage

from src.config.llm import get_llm
from src.config.settings import get_settings
from src.agents.state import SQLAgentState


# Schema检索提示词
SCHEMA_SELECTOR_PROMPT = """你是一个数据库专家。根据用户查询和数据库schema，识别相关的表。

## 可用表

{tables_info}

## 用户查询

{user_query}

## 任务

请返回与用户查询最相关的表名列表（用逗号分隔）。
只返回表名，不要其他内容。

例如: users, orders, products
"""


class SchemaRetriever:
    """数据库Schema检索器"""
    
    def __init__(self):
        self.settings = get_settings()
        self._pool: Optional[aiomysql.Pool] = None
    
    async def get_pool(self) -> aiomysql.Pool:
        """获取数据库连接池"""
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
    
    async def get_all_tables(self) -> list[str]:
        """获取所有表名"""
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SHOW TABLES")
                tables = await cur.fetchall()
                return [t[0] for t in tables]
    
    async def get_table_schema(self, table_name: str) -> dict[str, Any]:
        """获取单个表的schema信息"""
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                # 获取表结构
                await cur.execute(f"DESCRIBE `{table_name}`")
                columns = await cur.fetchall()
                
                # 获取表注释
                await cur.execute(f"""
                    SELECT TABLE_COMMENT 
                    FROM information_schema.TABLES 
                    WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                """, (self.settings.sandbox_db_name, table_name))
                comment_row = await cur.fetchone()
                table_comment = comment_row[0] if comment_row else ""
                
                return {
                    "table_name": table_name,
                    "comment": table_comment,
                    "columns": [
                        {
                            "name": col[0],
                            "type": col[1],
                            "nullable": col[2] == "YES",
                            "key": col[3],
                            "default": col[4],
                            "extra": col[5]
                        }
                        for col in columns
                    ]
                }
    
    async def get_full_schema(self) -> dict[str, Any]:
        """获取完整数据库schema"""
        tables = await self.get_all_tables()
        schema = {}
        for table in tables:
            schema[table] = await self.get_table_schema(table)
        return schema
    
    async def format_schema_for_llm(self, tables: list[str] = None) -> str:
        """格式化schema信息供LLM使用"""
        if tables is None:
            tables = await self.get_all_tables()
        
        output = []
        for table in tables:
            info = await self.get_table_schema(table)
            output.append(f"## 表: {table}")
            if info["comment"]:
                output.append(f"说明: {info['comment']}")
            output.append("字段:")
            for col in info["columns"]:
                pk = " [PRIMARY KEY]" if col["key"] == "PRI" else ""
                nullable = " (可为空)" if col["nullable"] else ""
                output.append(f"  - {col['name']}: {col['type']}{pk}{nullable}")
            output.append("")
        
        return "\n".join(output)
    
    async def close(self):
        """关闭连接池"""
        if self._pool:
            self._pool.close()
            await self._pool.wait_closed()
            self._pool = None


# 全局实例
_retriever: Optional[SchemaRetriever] = None


def get_schema_retriever() -> SchemaRetriever:
    """获取Schema检索器单例"""
    global _retriever
    if _retriever is None:
        _retriever = SchemaRetriever()
    return _retriever


async def schema_retriever_node(state: SQLAgentState) -> SQLAgentState:
    """
    Schema检索节点
    
    Args:
        state: 当前状态
        
    Returns:
        更新后的状态，包含schema信息
    """
    retriever = get_schema_retriever()
    llm = get_llm()
    
    user_query = state.get("user_query", "")
    
    try:
        # 获取所有表的简要信息
        all_tables = await retriever.get_all_tables()
        tables_brief = await retriever.format_schema_for_llm(all_tables[:20])  # 限制表数量
        
        # 使用LLM识别相关表
        prompt = SCHEMA_SELECTOR_PROMPT.format(
            tables_info=tables_brief,
            user_query=user_query
        )
        
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        relevant_tables = [t.strip() for t in response.content.split(",") if t.strip()]
        
        # 过滤有效表名
        relevant_tables = [t for t in relevant_tables if t in all_tables]
        
        # 如果没有识别到相关表，使用所有表
        if not relevant_tables:
            relevant_tables = all_tables[:10]
        
        # 获取相关表的详细schema
        schema_info = {}
        for table in relevant_tables:
            schema_info[table] = await retriever.get_table_schema(table)
        
        # 格式化schema供后续使用
        formatted_schema = await retriever.format_schema_for_llm(relevant_tables)
        
        return {
            **state,
            "schema_info": {
                "tables": schema_info,
                "formatted": formatted_schema
            },
            "relevant_tables": relevant_tables,
            "current_agent": "schema_retriever",
            "messages": [
                *state.get("messages", []),
                AIMessage(content=f"[Schema检索] 识别相关表: {', '.join(relevant_tables)}")
            ]
        }
        
    except Exception as e:
        return {
            **state,
            "schema_info": None,
            "relevant_tables": [],
            "current_agent": "schema_retriever",
            "error": f"Schema检索失败: {str(e)}"
        }
