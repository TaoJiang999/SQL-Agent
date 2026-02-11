from typing import List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, BaseMessage
from dotenv import load_dotenv
import os
from src.state import AgentState
from src.schema import SCHEMA_PROMPT

# Load environment variables
load_dotenv()

# Configure the model
model = ChatOpenAI(
    model=os.getenv("MODEL_NAME", "qwen-agent"),
    base_url=os.getenv("MODEL_BASE_URL", "http://localhost:8000/v1"),
    api_key=os.getenv("MODEL_API_KEY", "not-needed")
)

def call_model(state: AgentState):
    """
    Function to process user input and generate a response using the LLM.
    It injects the schema as a system prompt.
    """
    messages = state["messages"]
    
    # Check if we already have the system prompt inserted
    system_message_exists = any(isinstance(msg, SystemMessage) for msg in messages)
    
    call_messages = messages
    if not system_message_exists:
        # Prepend the system prompt containing the database schema
        call_messages = [SystemMessage(content=f"You are a helpful SQL assistant. Here is the database schema:\n{SCHEMA_PROMPT}")] + messages
    
    response = model.invoke(call_messages)
    return {"messages": [response]}

# Define the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("agent", call_model)

# Set entry point
workflow.set_entry_point("agent")

# Add edges
workflow.add_edge("agent", END)

# Compile the graph
graph = workflow.compile()
