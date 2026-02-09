"""
LLM 模型初始化模块

提供统一的 LLM 实例获取方法，所有 Agent 必须使用此模块获取 LLM
"""

import os
from functools import lru_cache
from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel


def get_llm(
    temperature: float | None = None,
    max_tokens: int | None = None
) -> BaseChatModel:
    """
    获取统一配置的 LLM 实例
    
    Args:
        temperature: 可选，覆盖默认温度参数
        max_tokens: 可选，覆盖默认最大token数
        
    Returns:
        BaseChatModel: 初始化后的 LLM 实例
        
    Example:
        >>> llm = get_llm()
        >>> response = await llm.ainvoke(messages)
    """
    return init_chat_model(
        model=os.getenv("MODEL_NAME"),
        model_provider=os.getenv("MODEL_PROVIDER"),
        api_key=os.getenv("MODEL_API_KEY"),
        base_url=os.getenv("MODEL_BASE_URL"),
        temperature=temperature or float(os.getenv("MODEL_TEMPERATURE", "0.7")),
        max_tokens=max_tokens or int(os.getenv("MODEL_MAX_TOKENS", "4096"))
    )


@lru_cache()
def get_cached_llm() -> BaseChatModel:
    """
    获取缓存的 LLM 实例（单例模式）
    
    适用于不需要动态调整参数的场景
    
    Returns:
        BaseChatModel: 缓存的 LLM 实例
    """
    return get_llm()
