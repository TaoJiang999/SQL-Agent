"""
SQL Agent Workflow Graph

Uses LangGraph to build SQL Agent processing flow:
Intent Classifier -> (chat) -> Chat Handler -> End
                 -> (sql)  -> Schema Retriever -> SQL Generator -> Executor
                                                       ^              |
                                                       |____(retry)___|
"""

from typing import Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage

from src.agents.state import SQLAgentState
from src.agents.workers.intent_classifier import intent_classifier_node
from src.agents.workers.schema_retriever import schema_retriever_node
from src.agents.workers.sql_generator import sql_generator_node
from src.agents.workers.sql_executor import sql_executor_node, should_retry
from src.agents.workers.chat_handler import chat_handler_node


def route_by_intent(state: SQLAgentState) -> str:
    """Route based on detected intent"""
    intent = state.get("intent", "chat")
    
    if intent == "chat":
        return "chat"
    elif intent in ["text_to_sql", "sql_to_text", "debug"]:
        return "sql"
    else:
        return "chat"  # Default to chat for unknown


def build_sql_agent_graph() -> StateGraph:
    """
    Build SQL Agent workflow graph
    
    Flow:
    1. Intent Classifier: Recognize user intent
    2. Route by intent:
       - chat: Go to Chat Handler -> End
       - sql/text_to_sql/debug: Go to Schema Retriever -> SQL Generator -> Executor
    3. If execution fails and retries remaining, go back to SQL Generator
    
    Returns:
        Compiled workflow graph
    """
    # Create state graph
    graph = StateGraph(SQLAgentState)
    
    # Add nodes
    graph.add_node("intent_classifier", intent_classifier_node)
    graph.add_node("chat_handler", chat_handler_node)
    graph.add_node("schema_retriever", schema_retriever_node)
    graph.add_node("sql_generator", sql_generator_node)
    graph.add_node("sql_executor", sql_executor_node)
    
    # Set entry point
    graph.set_entry_point("intent_classifier")
    
    # Add conditional edges: Intent Classifier -> Chat or SQL flow
    graph.add_conditional_edges(
        "intent_classifier",
        route_by_intent,
        {
            "chat": "chat_handler",
            "sql": "schema_retriever"
        }
    )
    
    # Chat handler -> End
    graph.add_edge("chat_handler", END)
    
    # SQL flow
    graph.add_edge("schema_retriever", "sql_generator")
    graph.add_edge("sql_generator", "sql_executor")
    
    # Executor -> End or retry
    graph.add_conditional_edges(
        "sql_executor",
        should_retry,
        {
            "retry": "sql_generator",
            "end": END
        }
    )
    
    # Compile graph
    return graph.compile()


async def run_sql_agent(user_input: str, max_retries: int = 3) -> dict:
    """Run SQL Agent workflow"""
    graph = build_sql_agent_graph()
    
    initial_state: SQLAgentState = {
        "messages": [HumanMessage(content=user_input)],
        "next": "",
        "task_result": None,
        "current_agent": None,
        "error": None,
        "intent": None,
        "intent_confidence": None,
        "user_query": user_input,
        "schema_info": None,
        "relevant_tables": None,
        "generated_sql": None,
        "sql_explanation": None,
        "execution_result": None,
        "execution_error": None,
        "retry_count": 0,
        "max_retries": max_retries
    }
    
    result = await graph.ainvoke(initial_state)
    
    return {
        "intent": result.get("intent"),
        "sql": result.get("generated_sql"),
        "explanation": result.get("sql_explanation"),
        "result": result.get("execution_result"),
        "error": result.get("execution_error") or result.get("error"),
        "retry_count": result.get("retry_count", 0),
        "tables_used": result.get("relevant_tables", [])
    }


# ==========================================
# Keep original generic workflow builders
# ==========================================

from src.agents.state import AgentState
from src.agents.supervisor.agent import SupervisorAgent, should_continue


def build_graph(worker_agents: dict) -> StateGraph:
    """Build multi-agent workflow graph (generic version)"""
    supervisor = SupervisorAgent(workers=list(worker_agents.keys()))
    
    graph = StateGraph(AgentState)
    
    async def supervisor_node(state: AgentState) -> AgentState:
        return await supervisor.route(state)
    
    graph.add_node("supervisor", supervisor_node)
    
    for name, agent in worker_agents.items():
        async def worker_node(state: AgentState, agent=agent) -> AgentState:
            return await agent.ainvoke(state)
        
        graph.add_node(name, worker_node)
    
    async def aggregate_node(state: AgentState) -> AgentState:
        return await supervisor.aggregate_results(state)
    
    graph.add_node("aggregate", aggregate_node)
    
    graph.set_entry_point("supervisor")
    
    graph.add_conditional_edges(
        "supervisor",
        should_continue,
        {
            "workers": list(worker_agents.keys())[0] if worker_agents else END,
            "aggregate": "aggregate",
            "end": END
        }
    )
    
    for name in worker_agents.keys():
        graph.add_edge(name, "supervisor")
    
    graph.add_edge("aggregate", END)
    
    return graph.compile()


async def run_workflow(graph, user_input: str) -> str:
    """Run workflow (generic version)"""
    initial_state = {
        "messages": [HumanMessage(content=user_input)],
        "next": "",
        "task_result": None,
        "current_agent": None,
        "error": None
    }
    
    result = await graph.ainvoke(initial_state)
    
    if result.get("messages"):
        return result["messages"][-1].content
    return "Unable to process your request"
