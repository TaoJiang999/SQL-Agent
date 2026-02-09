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
    
    # 沙盒数据库配置 (MySQL)
    sandbox_db_host: str = "localhost"
    sandbox_db_port: int = 3307
    sandbox_db_user: str = "sandbox_user"
    sandbox_db_password: str = "sandbox_password"
    sandbox_db_name: str = "ecommerce"
    
    # 日志配置
    log_level: str = "INFO"
    
    # 调试模式
    debug: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


# 导出配置实例
settings = get_settings()
