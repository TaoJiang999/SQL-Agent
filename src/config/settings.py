"""
项目配置管理

使用 pydantic-settings 进行配置管理，支持从环境变量加载配置
"""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用程序配置"""
    
    # LLM 配置
    model_name: str = "gpt-4"
    model_provider: str = "openai"
    model_api_key: str = "xxxxxx"
    model_base_url: str = "https://api.openai.com/v1"
    model_temperature: float = 0.7
    model_max_tokens: int = 4096
    
    # 数据库配置
    database_url: Optional[str] = None
    
    # 日志配置
    log_level: str = "INFO"
    
    # 调试模式
    debug: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


# 导出配置实例
settings = get_settings()
