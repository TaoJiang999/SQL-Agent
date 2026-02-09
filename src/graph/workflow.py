"""
多 Agent 工作流图定义

使用 LangGraph 构建 Supervisor-Worker 架构的工作流
"""

from typing import Literal
from langgraph.graph import StateGraph, END

from src.agents.state import AgentState
from src.agents.supervisor.agent import SupervisorAgent, should_continue


def build_graph(worker_agents: dict) -> StateGraph:
    """
    构建多 Agent 工作流图
    
    Args:
        worker_agents: Worker Agent 字典，key 为 agent 名称，value 为 agent 实例
        
    Returns:
        StateGraph: 编译后的工作流图
    """
    # 创建 Supervisor
    supervisor = SupervisorAgent(workers=list(worker_agents.keys()))
    
    # 创建状态图
    graph = StateGraph(AgentState)
    
    # 添加 Supervisor 节点
    async def supervisor_node(state: AgentState) -> AgentState:
        return await supervisor.route(state)
    
    graph.add_node("supervisor", supervisor_node)
    
    # 添加 Worker 节点
    for name, agent in worker_agents.items():
        async def worker_node(state: AgentState, agent=agent) -> AgentState:
            return await agent.ainvoke(state)
        
        graph.add_node(name, worker_node)
    
    # 添加汇总节点
    async def aggregate_node(state: AgentState) -> AgentState:
        return await supervisor.aggregate_results(state)
    
    graph.add_node("aggregate", aggregate_node)
    
    # 设置入口点
    graph.set_entry_point("supervisor")
    
    # 添加条件边：Supervisor -> Workers / Aggregate / End
    graph.add_conditional_edges(
        "supervisor",
        should_continue,
        {
            "workers": list(worker_agents.keys())[0] if worker_agents else END,
            "aggregate": "aggregate",
            "end": END
        }
    )
    
    # 添加边：Workers -> Supervisor（返回进行下一步决策）
    for name in worker_agents.keys():
        graph.add_edge(name, "supervisor")
    
    # 添加边：Aggregate -> End
    graph.add_edge("aggregate", END)
    
    # 编译图
    return graph.compile()


async def run_workflow(graph, user_input: str) -> str:
    """
    运行工作流
    
    Args:
        graph: 编译后的工作流图
        user_input: 用户输入
        
    Returns:
        str: 最终响应
    """
    from langchain_core.messages import HumanMessage
    
    initial_state = {
        "messages": [HumanMessage(content=user_input)],
        "next": "",
        "task_result": None,
        "current_agent": None,
        "error": None
    }
    
    # 异步执行工作流
    result = await graph.ainvoke(initial_state)
    
    # 返回最后一条消息内容
    if result.get("messages"):
        return result["messages"][-1].content
    return "无法处理您的请求"
