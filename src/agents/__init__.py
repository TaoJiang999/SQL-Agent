"""
多Agent系统模块

本项目采用 Supervisor-Worker 架构：
- Supervisor Agent: 负责任务理解、分发和结果汇总
- Worker Agents: 负责执行具体的专项任务
"""

from .state import AgentState
from .base import BaseAgent

__all__ = ["AgentState", "BaseAgent"]
