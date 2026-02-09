"""
示例 Worker Agent 实现

这是一个 Worker Agent 的模板，展示了如何正确实现一个 Worker Agent
"""

from typing import Any
from langchain_core.messages import SystemMessage, AIMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

from src.config.llm import get_llm
from src.agents.base import BaseAgent
from src.agents.state import AgentState


# ==========================================
# 工具定义
# ==========================================

@tool
async def example_tool(query: str) -> str:
    """
    示例工具
    
    Args:
        query: 查询字符串
        
    Returns:
        str: 工具执行结果
    """
    # 实现工具逻辑
    return f"处理查询: {query}"


# ==========================================
# 提示词定义
# ==========================================

EXAMPLE_AGENT_PROMPT = """你是一个示例 Worker Agent。

你的职责是：
1. 处理 Supervisor 分配给你的任务
2. 使用可用的工具完成任务
3. 返回清晰的执行结果

请尽力完成分配的任务。
"""


# ==========================================
# Agent 实现
# ==========================================

class ExampleAgent(BaseAgent):
    """示例 Worker Agent"""
    
    def __init__(self):
        super().__init__(
            name="example_agent",
            description="这是一个示例 Agent，展示如何实现 Worker Agent",
            tools=[example_tool]
        )
        
        # 创建 ReAct Agent
        self._agent = create_react_agent(
            self.llm,
            self.tools,
            prompt=EXAMPLE_AGENT_PROMPT
        )
    
    def get_system_prompt(self) -> str:
        return EXAMPLE_AGENT_PROMPT
    
    async def ainvoke(self, state: AgentState) -> AgentState:
        """
        异步执行 Agent
        
        Args:
            state: 当前状态
            
        Returns:
            AgentState: 更新后的状态
        """
        # 使用异步调用 (必须使用 ainvoke)
        result = await self._agent.ainvoke({
            "messages": state["messages"]
        })
        
        return {
            **state,
            "messages": result["messages"],
            "current_agent": self.name,
            "task_result": {
                "agent": self.name,
                "status": "success",
                "output": result["messages"][-1].content if result["messages"] else ""
            }
        }


async def create_example_agent():
    """
    工厂函数：创建示例 Agent
    
    Returns:
        编译后的 Agent 图
    """
    llm = get_llm()
    tools = [example_tool]
    
    agent = create_react_agent(
        llm,
        tools,
        prompt=EXAMPLE_AGENT_PROMPT
    )
    
    return agent
