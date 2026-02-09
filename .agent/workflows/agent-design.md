---
description: 多Agent项目设计规范和开发指南
---

# 多Agent项目设计规范

## 项目架构概述

本项目采用 **Supervisor-Worker** 架构模式：
- **Supervisor Agent (主Agent)**：负责任务理解、分发和结果汇总
- **Worker Agents (子Agent)**：负责执行具体的专项任务

## Agent 创建规范

### 1. LLM 模型初始化

所有 Agent 在创建时 **必须** 使用以下标准方式初始化 LLM：

```python
import os
from langchain.chat_models import init_chat_model

def get_llm():
    """获取统一配置的 LLM 实例"""
    return init_chat_model(
        model=os.getenv("MODEL_NAME"),
        model_provider=os.getenv("MODEL_PROVIDER"),
        api_key=os.getenv("MODEL_API_KEY"),
        base_url=os.getenv("MODEL_BASE_URL"),
        temperature=float(os.getenv("MODEL_TEMPERATURE", "0.7")),
        max_tokens=int(os.getenv("MODEL_MAX_TOKENS", "4096"))
    )
```

### 2. 异步调用规范

所有 Agent 的调用 **必须** 使用异步 `ainvoke` 方法：

```python
# ✅ 正确方式：使用异步调用
result = await agent.ainvoke({"messages": messages})

# ❌ 错误方式：同步调用
result = agent.invoke({"messages": messages})
```

### 3. Agent 函数定义规范

```python
async def create_agent(
    llm,
    tools: list,
    system_prompt: str
) -> CompiledGraph:
    """
    创建标准化的 Agent
    
    Args:
        llm: 语言模型实例
        tools: Agent 可用的工具列表
        system_prompt: 系统提示词
        
    Returns:
        CompiledGraph: 编译后的 Agent 图
    """
    pass
```

## Supervisor Agent 设计规范

### 1. 职责定义
- 接收并理解用户任务
- 分析任务并拆分为子任务
- 选择合适的 Worker Agent 执行任务
- 汇总子任务结果并生成最终响应

### 2. 代码模板

```python
from typing import Literal
from langchain_core.messages import HumanMessage

async def supervisor_node(state: AgentState) -> AgentState:
    """Supervisor 决策节点"""
    llm = get_llm()
    
    # 定义可用的 worker agents
    workers = ["sql_agent", "analysis_agent", "report_agent"]
    
    response = await llm.ainvoke(
        system_prompt + f"\n可用的工作代理: {workers}",
        messages=state["messages"]
    )
    
    return {"next": response.next_agent, "messages": state["messages"]}
```

## Worker Agent 设计规范

### 1. 目录结构
每个 Worker Agent 应该有独立的目录：

```
agents/
├── supervisor/
│   ├── __init__.py
│   ├── agent.py
│   └── prompts.py
├── sql_agent/
│   ├── __init__.py
│   ├── agent.py
│   ├── tools.py
│   └── prompts.py
└── analysis_agent/
    ├── __init__.py
    ├── agent.py
    ├── tools.py
    └── prompts.py
```

### 2. Worker Agent 模板

```python
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

async def create_sql_agent():
    """创建 SQL Agent"""
    llm = get_llm()
    tools = [execute_sql, get_schema, validate_query]
    
    agent = create_react_agent(
        llm,
        tools,
        prompt=SQL_AGENT_PROMPT
    )
    return agent
```

## 工具定义规范

### 1. 使用 @tool 装饰器

```python
from langchain_core.tools import tool

@tool
async def execute_sql(query: str) -> str:
    """
    执行 SQL 查询
    
    Args:
        query: SQL 查询语句
        
    Returns:
        查询结果的字符串表示
    """
    # 实现逻辑
    pass
```

### 2. 工具命名规范
- 使用小写字母和下划线
- 名称应该清晰描述工具功能
- 例如：`execute_sql`, `get_table_schema`, `generate_report`

## 状态管理规范

### 1. 定义统一的状态类型

```python
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """Agent 状态定义"""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    next: str  # 下一个要执行的 agent
    task_result: dict  # 任务执行结果
```

## 错误处理规范

### 1. 使用统一的异常处理

```python
async def safe_agent_invoke(agent, state):
    """安全的 Agent 调用封装"""
    try:
        result = await agent.ainvoke(state)
        return result
    except Exception as e:
        logger.error(f"Agent 执行失败: {e}")
        return {"error": str(e), "messages": state["messages"]}
```

## 环境变量配置

确保 `.env` 文件包含以下配置：

```bash
# LLM 配置
MODEL_NAME=gpt-4
MODEL_PROVIDER=openai
MODEL_API_KEY=your-api-key
MODEL_BASE_URL=https://api.openai.com/v1
MODEL_TEMPERATURE=0.7
MODEL_MAX_TOKENS=4096

# 数据库配置 (如需要)
DATABASE_URL=postgresql://user:pass@localhost:5432/db
```
