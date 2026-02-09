"""
Agent 基类模块

提供所有 Agent 的基础实现
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool

from src.config.llm import get_llm
from .state import AgentState


class BaseAgent(ABC):
    """
    Agent 基类
    
    所有 Worker Agent 都应该继承此类
    
    Attributes:
        name: Agent 名称
        description: Agent 描述
        llm: 语言模型实例
        tools: Agent 可用的工具列表
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        tools: Optional[list[BaseTool]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ):
        """
        初始化 Agent
        
        Args:
            name: Agent 名称
            description: Agent 描述
            tools: 可选，Agent 使用的工具列表
            temperature: 可选，LLM 温度参数
            max_tokens: 可选，LLM 最大 token 数
        """
        self.name = name
        self.description = description
        self.tools = tools or []
        self.llm = get_llm(temperature=temperature, max_tokens=max_tokens)
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        获取系统提示词
        
        Returns:
            str: 系统提示词
        """
        pass
    
    @abstractmethod
    async def ainvoke(self, state: AgentState) -> AgentState:
        """
        异步执行 Agent
        
        所有 Agent 必须实现异步调用方法
        
        Args:
            state: 当前 Agent 状态
            
        Returns:
            AgentState: 更新后的状态
        """
        pass
    
    async def safe_invoke(self, state: AgentState) -> AgentState:
        """
        安全的异步调用封装
        
        自动处理异常并更新状态中的错误信息
        
        Args:
            state: 当前 Agent 状态
            
        Returns:
            AgentState: 更新后的状态（包含错误信息如果有）
        """
        try:
            return await self.ainvoke(state)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Agent '{self.name}' 执行失败: {e}")
            return {
                **state,
                "error": str(e),
                "current_agent": self.name
            }
