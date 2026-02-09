"""
SQL Agent 入口

供 LangGraph Studio 使用
"""

from src.graph.workflow import build_sql_agent_graph

# 构建图 - 供 LangGraph Studio 使用
graph = build_sql_agent_graph()
