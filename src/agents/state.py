"""
Agent 状态定义模块

定义所有 Agent 共享的状态结构
"""

from typing import TypedDict, Annotated, Sequence, Any, Optional, Literal
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


# Intent Type
IntentType = Literal["text_to_sql", "sql_to_text", "debug", "chat", "unknown"]


class AgentState(TypedDict):
    """
    Agent 状态定义
    
    Attributes:
        messages: 消息历史，使用 add_messages 确保正确追加
        next: 下一个要执行的 agent 名称
        task_result: 任务执行结果
        current_agent: 当前正在执行的 agent
        error: 错误信息（如果有）
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]
    next: str
    task_result: Optional[dict[str, Any]]
    current_agent: Optional[str]
    error: Optional[str]


class SQLAgentState(AgentState):
    """
    SQL Agent 专用状态
    
    Attributes:
        intent: 识别的用户意图类型
        intent_confidence: 意图识别置信度
        user_query: 用户原始查询
        schema_info: 数据库 schema 信息
        relevant_tables: 相关表列表
        generated_sql: 生成的 SQL 语句
        sql_explanation: SQL 解释（用于 sql_to_text）
        execution_result: SQL 执行结果
        execution_error: 执行错误信息
        retry_count: 重试次数
        max_retries: 最大重试次数
    """
    intent: Optional[IntentType]
    intent_confidence: Optional[float]
    user_query: Optional[str]
    schema_info: Optional[dict[str, Any]]
    relevant_tables: Optional[list[str]]
    generated_sql: Optional[str]
    sql_explanation: Optional[str]
    execution_result: Optional[dict[str, Any]]
    execution_error: Optional[str]
    retry_count: int
    max_retries: int


class SupervisorState(AgentState):
    """
    Supervisor 专用状态
    
    继承自 AgentState，添加 Supervisor 特有的状态字段
    """
    available_workers: list[str]  # 可用的 worker agent 列表
    task_plan: Optional[list[dict]]  # 任务计划
    completed_tasks: list[str]  # 已完成的任务列表

