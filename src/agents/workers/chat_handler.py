"""
Chat Handler - General Conversation Node

Handles non-database related conversations
"""

from langchain_core.messages import HumanMessage, AIMessage

from src.config.llm import get_llm
from src.agents.state import SQLAgentState


CHAT_SYSTEM_PROMPT = """You are a helpful AI assistant. You can help with:
- General questions and conversations
- Explaining concepts
- Providing information

If the user asks about database queries or SQL, remind them that you can also help with:
- Converting natural language to SQL queries
- Explaining SQL statements
- Debugging SQL errors

Always respond in the same language as the user's input.
"""


async def chat_handler_node(state: SQLAgentState) -> SQLAgentState:
    """
    Chat handler node for general conversation
    
    Args:
        state: Current state
        
    Returns:
        Updated state with chat response
    """
    llm = get_llm()
    user_query = state.get("user_query", "")
    messages = state.get("messages", [])
    
    try:
        # Build conversation context
        chat_messages = [
            HumanMessage(content=CHAT_SYSTEM_PROMPT),
            HumanMessage(content=user_query)
        ]
        
        response = await llm.ainvoke(chat_messages)
        
        return {
            **state,
            "current_agent": "chat_handler",
            "messages": [
                *messages,
                AIMessage(content=response.content)
            ],
            "task_result": {
                "success": True,
                "type": "chat",
                "response": response.content
            }
        }
        
    except Exception as e:
        return {
            **state,
            "current_agent": "chat_handler",
            "messages": [
                *messages,
                AIMessage(content=f"Sorry, I encountered an error: {str(e)}")
            ],
            "error": str(e)
        }
