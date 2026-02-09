"""
Agent 状态定义模块

定义所有 Agent 共享的状态结构
"""

from typing import TypedDict, Annotated, Sequence, Any, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


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


class SupervisorState(AgentState):
    """
    Supervisor 专用状态
    
    继承自 AgentState，添加 Supervisor 特有的状态字段
    """
    available_workers: list[str]  # 可用的 worker agent 列表
    task_plan: Optional[list[dict]]  # 任务计划
    completed_tasks: list[str]  # 已完成的任务列表
