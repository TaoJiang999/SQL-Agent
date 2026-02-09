# SQL Agent - 多Agent协作系统

采用 **Supervisor-Worker** 架构的多Agent协作系统。

## 项目架构

```
┌─────────────────────────────────────────────────────────┐
│                    Supervisor Agent                      │
│              (任务理解、分发、结果汇总)                    │
└────────────────────────┬────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ SQL Agent   │  │ Analysis    │  │ Report      │
│             │  │ Agent       │  │ Agent       │
└─────────────┘  └─────────────┘  └─────────────┘
```

## 目录结构

```
sql-agent/
├── .agent/
│   └── workflows/          # 工作流定义
│       └── agent-design.md # Agent设计规范
├── src/
│   ├── config/            # 配置模块
│   │   ├── settings.py    # 项目设置
│   │   └── llm.py         # LLM初始化
│   ├── agents/            # Agent模块
│   │   ├── state.py       # 状态定义
│   │   ├── base.py        # Agent基类
│   │   ├── supervisor/    # Supervisor Agent
│   │   └── workers/       # Worker Agents
│   └── graph/             # LangGraph工作流
│       └── workflow.py    # 工作流定义
├── tests/                 # 测试文件
├── .env.example          # 环境变量示例
├── pyproject.toml        # 项目配置
└── README.md
```

## 快速开始

### 1. 安装依赖

```bash
pip install -e .
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的配置
```

### 3. 运行示例

```python
import asyncio
from src.graph.workflow import build_graph, run_workflow
from src.agents.workers.example_agent import ExampleAgent

async def main():
    # 创建 Worker Agents
    workers = {
        "example_agent": ExampleAgent()
    }
    
    # 构建工作流图
    graph = build_graph(workers)
    
    # 运行工作流
    result = await run_workflow(graph, "你好，请帮我处理一个任务")
    print(result)

asyncio.run(main())
```

## 设计规范

详细的设计规范请参考 [.agent/workflows/agent-design.md](.agent/workflows/agent-design.md)

### 核心原则

1. **统一的LLM初始化**：所有Agent必须使用 `src/config/llm.py` 中的 `get_llm()` 函数
2. **异步调用**：所有Agent调用必须使用 `ainvoke` 异步方法
3. **状态管理**：使用统一的 `AgentState` 定义

## License

MIT
