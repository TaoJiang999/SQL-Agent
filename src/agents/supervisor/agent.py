"""
Supervisor Agent 实现

负责任务调度和结果汇总的主 Agent
"""

from typing import Literal, Any
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel

from src.config.llm import get_llm
from ..state import AgentState, SupervisorState
from .prompts import SUPERVISOR_SYSTEM_PROMPT


class RouterOutput(BaseModel):
    """路由输出模型"""
    next: str
    reasoning: str


class SupervisorAgent:
    """
    Supervisor Agent
    
    负责理解用户任务、分发到合适的 Worker Agent、汇总结果
    """
    
    def __init__(self, workers: list[str]):
        """
        初始化 Supervisor Agent
        
        Args:
            workers: 可用的 worker agent 名称列表
        """
        self.workers = workers
        self.llm = get_llm()
        self.system_prompt = SUPERVISOR_SYSTEM_PROMPT.format(
            workers="\n".join([f"- {w}" for w in workers])
        )
    
    async def route(self, state: AgentState) -> dict[str, Any]:
        """
        路由决策：决定下一步由哪个 Agent 执行
        
        Args:
            state: 当前状态
            
        Returns:
            dict: 包含 next 字段的路由决策
        """
        messages = [
            SystemMessage(content=self.system_prompt),
            *state["messages"]
        ]
        
        # 使用结构化输出获取路由决策
        structured_llm = self.llm.with_structured_output(RouterOutput)
        response = await structured_llm.ainvoke(messages)
        
        return {
            "next": response.next,
            "current_agent": "supervisor"
        }
    
    async def aggregate_results(
        self, 
        state: SupervisorState
    ) -> dict[str, Any]:
        """
        汇总所有 Worker Agent 的执行结果
        
        Args:
            state: 当前状态（包含任务结果）
            
        Returns:
            dict: 汇总后的最终结果
        """
        from .prompts import RESULT_AGGREGATION_PROMPT
        
        # 构建结果汇总消息
        task_results = state.get("task_result", {})
        prompt = RESULT_AGGREGATION_PROMPT.format(
            original_request=state["messages"][0].content if state["messages"] else "",
            task_results=str(task_results)
        )
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        
        return {
            "messages": [response],
            "next": "FINISH"
        }


def should_continue(state: AgentState) -> Literal["workers", "aggregate", "end"]:
    """
    条件边：决定图的下一步走向
    
    Args:
        state: 当前状态
        
    Returns:
        下一步的目标节点
    """
    next_agent = state.get("next", "")
    
    if next_agent == "FINISH":
        return "end"
    elif next_agent == "AGGREGATE":
        return "aggregate"
    else:
        return "workers"
