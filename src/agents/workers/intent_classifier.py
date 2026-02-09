"""
Intent Classifier - Intent Recognition Node

Identifies user input intent:
- text_to_sql: Natural language to SQL
- sql_to_text: Explain SQL statement
- debug: SQL debugging/fixing
- chat: General conversation (non-database related)
"""

import re
import json
from typing import Any
from langchain_core.messages import HumanMessage, AIMessage

from src.config.llm import get_llm
from src.agents.state import SQLAgentState, IntentType


INTENT_CLASSIFIER_PROMPT = """你是一个意图分类专家。分析用户输入并确定其意图类型。

## 意图类型

1. **text_to_sql**: 用户想要根据自然语言生成SQL查询
   - 示例: "查询价格大于100的商品", "帮我统计各类别的销量", "有多少用户"
   - 关键词: 查询、统计、列出、显示、多少、哪些、获取数据
   
2. **sql_to_text**: 用户想要理解SQL语句的含义
   - 示例: "解释这个SQL: SELECT ...", "这个查询是什么意思?"
   - 关键词: 解释、理解、什么意思、SQL含义
   
3. **debug**: 用户想要调试或修复有问题的SQL
   - 示例: "这个SQL有错误，请帮忙", "为什么查询没有结果?"
   - 关键词: 错误、修复、调试、报错、失败

4. **chat**: 一般对话，与数据库或SQL无关
   - 示例: "你好", "今天天气怎么样?", "讲个笑话", "你是谁?"
   - 任何不涉及数据库查询、SQL或数据分析的问题

## 判断规则

- 如果用户提到"查询"、"统计"、"多少"、"列出"等词汇，通常是 text_to_sql
- 如果用户输入包含 SELECT、FROM、WHERE 等SQL关键字并询问含义，是 sql_to_text
- 如果用户明确提到"错误"、"修复"、"调试"，是 debug
- 只有完全与数据库无关的闲聊才是 chat

## 用户输入

{user_input}

## 输出格式

请用JSON格式输出:
```json
{{
    "intent": "text_to_sql|sql_to_text|debug|chat",
    "confidence": 0.0-1.0,
    "reasoning": "分类原因"
}}
```
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
    
    # Get latest user message
    messages = state.get("messages", [])
    user_input = ""
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            content = msg.content
            # Handle multimodal content (list of dicts)
            if isinstance(content, list):
                # Extract text from list content
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        user_input = item.get("text", "")
                        break
                    elif isinstance(item, str):
                        user_input = item
                        break
            else:
                user_input = content
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
    
    # Quick pattern matching for obvious cases
    quick_intent = quick_classify(user_input)
    if quick_intent:
        print(f"[Intent] Quick match: {quick_intent} for: {user_input[:50]}")
        return {
            **state,
            "intent": quick_intent,
            "intent_confidence": 0.9,
            "user_query": user_input,
            "current_agent": "intent_classifier",
        }
    
    # Call LLM for intent classification
    prompt = INTENT_CLASSIFIER_PROMPT.format(user_input=user_input)
    
    try:
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        result = parse_json_response(response.content)
        
        intent = result.get("intent", "text_to_sql")
        confidence = result.get("confidence", 0.8)
        
        # Validate intent
        if intent not in ["text_to_sql", "sql_to_text", "debug", "chat"]:
            intent = "text_to_sql"  # Default to text_to_sql for unknown
        
        print(f"[Intent] LLM classified: {intent} (confidence: {confidence}) for: {user_input[:50]}")
        
        return {
            **state,
            "intent": intent,
            "intent_confidence": confidence,
            "user_query": user_input,
            "current_agent": "intent_classifier",
        }
        
    except Exception as e:
        print(f"[Intent] Error: {e}, falling back to text_to_sql")
        # On error, default to text_to_sql (safer for database queries)
        return {
            **state,
            "intent": "text_to_sql",
            "intent_confidence": 0.5,
            "user_query": user_input,
            "current_agent": "intent_classifier",
        }


def quick_classify(user_input: str) -> str | None:
    """
    Quick pattern-based classification for obvious cases
    Returns intent or None if uncertain
    """
    input_lower = user_input.lower()
    
    # SQL query patterns (text_to_sql)
    sql_keywords = [
        "查询", "统计", "列出", "显示", "多少", "哪些", "获取",
        "查找", "搜索", "筛选", "排序", "分组", "汇总", "计算",
        "求和", "平均", "最大", "最小", "总数", "数量",
        "用户", "商品", "订单", "销量", "价格", "库存"
    ]
    
    # SQL explanation patterns (sql_to_text)
    explain_keywords = ["解释", "什么意思", "这个sql", "这个查询"]
    
    # Debug patterns
    debug_keywords = ["错误", "修复", "调试", "报错", "失败", "不对", "问题"]
    
    # Chat patterns (only pure greetings)
    chat_patterns = [
        r"^(你好|hi|hello|嗨|早上好|晚上好|下午好)[\s!！。.]*$",
        r"^(今天天气|讲个笑话|你是谁|介绍一下自己)",
        r"^(谢谢|再见|拜拜|bye)",
    ]
    
    # Check for SQL keywords first (high priority)
    for keyword in sql_keywords:
        if keyword in input_lower:
            return "text_to_sql"
    
    # Check for SELECT/SQL in input
    if re.search(r'\bSELECT\b', user_input, re.IGNORECASE):
        for kw in explain_keywords:
            if kw in input_lower:
                return "sql_to_text"
        return "text_to_sql"
    
    # Check debug
    for keyword in debug_keywords:
        if keyword in input_lower:
            return "debug"
    
    # Check pure chat
    for pattern in chat_patterns:
        if re.match(pattern, input_lower):
            return "chat"
    
    # Uncertain, let LLM decide
    return None


def parse_json_response(content: str) -> dict:
    """Parse JSON from LLM response, handling markdown code blocks"""
    # Try to extract JSON from code block
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
    if json_match:
        return json.loads(json_match.group(1))
    
    # Try to find raw JSON
    json_match = re.search(r'\{[^{}]*"intent"[^{}]*\}', content, re.DOTALL)
    if json_match:
        return json.loads(json_match.group())
    
    # Last resort: parse entire content
    return json.loads(content)
