"""
SQL Generator - SQL生成/翻译/修复节点

负责：
- text_to_sql: 根据schema和用户查询生成SQL
- sql_to_text: 解释SQL语句含义
- debug: 根据错误信息修复SQL
"""

from typing import Any
from langchain_core.messages import AIMessage, HumanMessage

from src.config.llm import get_llm
from src.agents.state import SQLAgentState


# Text-to-SQL 提示词
TEXT_TO_SQL_PROMPT = """你是一个专业的SQL生成专家。根据用户需求和数据库schema生成正确的MySQL SQL语句。

## 数据库Schema

{schema}

## 用户需求

{user_query}

## 要求

1. 只生成SELECT查询，不要生成INSERT/UPDATE/DELETE
2. 使用正确的表名和字段名
3. 考虑JOIN关系和外键约束
4. 添加适当的WHERE条件和排序
5. 只返回SQL语句，不要其他解释

## SQL语句
"""

# SQL-to-Text 提示词
SQL_TO_TEXT_PROMPT = """你是一个SQL解释专家。用通俗易懂的中文解释这个SQL语句的作用。

## 数据库Schema

{schema}

## SQL语句

{sql}

## 解释要求

1. 说明查询的目的
2. 解释涉及的表和字段
3. 说明筛选条件和排序
4. 用业务语言描述结果

## 解释
"""

# Debug 提示词
DEBUG_SQL_PROMPT = """你是一个SQL调试专家。根据错误信息修复SQL语句。

## 数据库Schema

{schema}

## 原始SQL

{sql}

## 错误信息

{error}

## 修复要求

1. 分析错误原因
2. 修复SQL语句
3. 只返回修复后的SQL语句

## 修复后的SQL
"""


async def sql_generator_node(state: SQLAgentState) -> SQLAgentState:
    """
    SQL生成节点
    
    根据意图类型执行不同的生成任务
    
    Args:
        state: 当前状态
        
    Returns:
        更新后的状态
    """
    llm = get_llm()
    intent = state.get("intent", "unknown")
    user_query = state.get("user_query", "")
    schema_info = state.get("schema_info", {})
    formatted_schema = schema_info.get("formatted", "") if schema_info else ""
    
    # 获取已有的SQL（用于debug模式）
    existing_sql = state.get("generated_sql", "")
    execution_error = state.get("execution_error", "")
    retry_count = state.get("retry_count", 0)
    
    try:
        if intent == "text_to_sql":
            # 自然语言转SQL
            prompt = TEXT_TO_SQL_PROMPT.format(
                schema=formatted_schema,
                user_query=user_query
            )
            response = await llm.ainvoke([HumanMessage(content=prompt)])
            generated_sql = response.content.strip()
            
            # 清理SQL（移除markdown代码块标记）
            if generated_sql.startswith("```"):
                lines = generated_sql.split("\n")
                generated_sql = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
            
            return {
                **state,
                "generated_sql": generated_sql.strip(),
                "current_agent": "sql_generator",
                "messages": [
                    *state.get("messages", []),
                    AIMessage(content=f"[SQL生成] 已生成SQL查询")
                ]
            }
            
        elif intent == "sql_to_text":
            # SQL转自然语言
            # 从用户查询中提取SQL
            sql_to_explain = user_query
            if "SELECT" in user_query.upper():
                # 尝试提取SQL部分
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
                "messages": [
                    *state.get("messages", []),
                    AIMessage(content=f"[SQL解释] {response.content.strip()}")
                ]
            }
            
        elif intent == "debug" or execution_error:
            # 调试/修复模式
            sql_to_fix = existing_sql or user_query
            error_msg = execution_error or "未知错误"
            
            prompt = DEBUG_SQL_PROMPT.format(
                schema=formatted_schema,
                sql=sql_to_fix,
                error=error_msg
            )
            response = await llm.ainvoke([HumanMessage(content=prompt)])
            fixed_sql = response.content.strip()
            
            # 清理SQL
            if fixed_sql.startswith("```"):
                lines = fixed_sql.split("\n")
                fixed_sql = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
            
            return {
                **state,
                "generated_sql": fixed_sql.strip(),
                "execution_error": None,  # 清除错误，准备重试
                "retry_count": retry_count + 1,
                "current_agent": "sql_generator",
                "messages": [
                    *state.get("messages", []),
                    AIMessage(content=f"[SQL修复] 第{retry_count + 1}次修复尝试")
                ]
            }
            
        else:
            return {
                **state,
                "current_agent": "sql_generator",
                "error": f"未知意图类型: {intent}"
            }
            
    except Exception as e:
        return {
            **state,
            "current_agent": "sql_generator",
            "error": f"SQL生成失败: {str(e)}"
        }
