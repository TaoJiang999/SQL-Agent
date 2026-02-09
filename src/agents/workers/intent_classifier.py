"""
Intent Classifier - Intent Recognition Node

Identifies user input intent:
- text_to_sql: Natural language to SQL
- sql_to_text: Explain SQL statement
- debug: SQL debugging/fixing
- chat: General conversation (non-database related)
"""

from typing import Any
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from src.config.llm import get_llm
from src.agents.state import SQLAgentState, IntentType


class IntentResult(BaseModel):
    """Intent recognition result"""
    intent: str = Field(description="Intent type: text_to_sql, sql_to_text, debug, chat")
    confidence: float = Field(description="Confidence 0-1")
    reasoning: str = Field(description="Recognition reasoning")


INTENT_CLASSIFIER_PROMPT = """You are an intent classification expert. Analyze user input and determine its intent type.

## Intent Types

1. **text_to_sql**: User wants to convert natural language to SQL query
   - Examples: "Query all products with price greater than 100", "Help me count sales by category"
   
2. **sql_to_text**: User wants to understand the meaning of an SQL statement
   - Examples: "Explain this SQL: SELECT ...", "What does this query mean?"
   
3. **debug**: User wants to debug or fix problematic SQL
   - Examples: "This SQL has errors, please help", "Why does this query return no results?"

4. **chat**: General conversation, NOT related to database or SQL
   - Examples: "Hello", "What's the weather today?", "Tell me a joke", "Who are you?"
   - Any question that does NOT involve database queries, SQL, or data analysis

## Output Format

Please output in JSON format:
```json
{{
    "intent": "text_to_sql|sql_to_text|debug|chat",
    "confidence": 0.0-1.0,
    "reasoning": "Reason for classification"
}}
```

## User Input

{user_input}
"""


async def intent_classifier_node(state: SQLAgentState) -> SQLAgentState:
    """
    Intent classification node
    
    Args:
        state: Current state
        
    Returns:
        Updated state with recognized intent
    """
    llm = get_llm()
    parser = JsonOutputParser(pydantic_object=IntentResult)
    
    # Get latest user message
    messages = state.get("messages", [])
    user_input = ""
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            user_input = msg.content
            break
    
    if not user_input:
        return {
            **state,
            "intent": "unknown",
            "intent_confidence": 0.0,
            "user_query": "",
            "current_agent": "intent_classifier",
            "error": "No user input found"
        }
    
    # Call LLM for intent classification
    prompt = INTENT_CLASSIFIER_PROMPT.format(user_input=user_input)
    
    try:
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        result = parser.parse(response.content)
        
        intent = result.get("intent", "chat")
        if intent not in ["text_to_sql", "sql_to_text", "debug", "chat"]:
            intent = "chat"  # Default to chat for unknown intents
        
        return {
            **state,
            "intent": intent,
            "intent_confidence": result.get("confidence", 0.0),
            "user_query": user_input,
            "current_agent": "intent_classifier",
        }
        
    except Exception as e:
        # On error, default to chat mode
        return {
            **state,
            "intent": "chat",
            "intent_confidence": 0.5,
            "user_query": user_input,
            "current_agent": "intent_classifier",
        }
