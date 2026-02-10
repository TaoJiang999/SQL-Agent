# 🤖 SQL-Agent — 基于 LangGraph 的智能 SQL 多 Agent 协作系统

<p align="center">
  <strong>自然语言 → SQL 查询 → 自动执行 → 结果解读，一站式完成</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/LangGraph-0.2+-green?logo=langchain" alt="LangGraph">
  <img src="https://img.shields.io/badge/MySQL-8.0-orange?logo=mysql" alt="MySQL">
  <img src="https://img.shields.io/badge/Docker-Required-blue?logo=docker" alt="Docker">
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License">
</p>

---

## ✨ 项目亮点

- 🧠 **多 Agent 协作架构** — 采用 Supervisor-Worker 模式，多个专业 Agent 分工协作，各司其职
- 🎯 **智能意图识别** — 自动区分自然语言闲聊与 SQL 查询需求，精准路由
- 🔍 **RAG 增强生成** — 基于 FAISS 向量检索，利用历史 SQL 示例指导生成，提升准确率
- 🛡️ **安全沙箱执行** — SQL 在隔离的 Docker MySQL 容器中执行，保障数据安全
- 🔄 **自动纠错重试** — SQL 执行失败时自动分析错误原因并重新生成，最多重试 3 次
- 🚀 **灵活模型部署** — 支持云端 API（OpenAI / Google / 第三方）和本地 vLLM 部署两种方式
- 📊 **LangGraph Studio** — 可通过 `langgraph dev` 可视化调试 Agent 工作流
- 🔗 **LangSmith 追踪** — 内置 LangSmith 链路追踪，方便调试与性能分析

---

## 🏗️ Agent 架构

```
                        ┌──────────────────────────┐
                        │       用户输入 (Query)      │
                        └─────────────┬────────────┘
                                      ▼
                        ┌──────────────────────────┐
                        │    🎯 Intent Classifier    │
                        │      (意图识别 Agent)       │
                        └──────┬──────────────┬────┘
                               │              │
                          chat │              │ sql / text_to_sql / debug
                               ▼              ▼
                  ┌─────────────────┐  ┌──────────────────┐
                  │  💬 Chat Handler │  │ 🔍 Schema Retriever│
                  │   (闲聊处理器)    │  │  (Schema 检索器)   │
                  └────────┬────────┘  └────────┬─────────┘
                           │                    │
                           ▼                    ▼
                        结束输出          ┌──────────────────┐
                                        │ ⚡ SQL Generator   │◄──── RAG 向量检索
                                        │  (SQL 生成器)      │     (FAISS + 历史示例)
                                        └────────┬─────────┘
                                                 │
                                                 ▼
                                        ┌──────────────────┐
                                        │ 🛡️ SQL Executor   │
                                        │ (安全沙箱执行器)    │
                                        └───┬──────────┬───┘
                                            │          │
                                       成功  │          │ 失败 (retry < max)
                                            ▼          ▼
                                        结果输出    回到 SQL Generator
```

---

## 📁 目录结构

```
SQL-Agent/
├── main.py                        # 入口文件 (LangGraph Studio)
├── langgraph.json                 # LangGraph 配置
├── pyproject.toml                 # 项目依赖配置
├── .env.example                   # 环境变量示例
│
├── src/                           # 源码目录
│   ├── __init__.py
│   ├── config/                    # 配置模块
│   │   ├── settings.py            #   项目设置 (Pydantic Settings)
│   │   └── llm.py                 #   LLM 统一初始化
│   │
│   ├── agents/                    # Agent 模块
│   │   ├── state.py               #   状态定义 (AgentState / SQLAgentState)
│   │   ├── base.py                #   Agent 基类
│   │   ├── supervisor/            #   Supervisor Agent
│   │   │   ├── agent.py           #     路由决策 & 结果汇总
│   │   │   └── prompts.py         #     系统提示词
│   │   └── workers/               #   Worker Agents
│   │       ├── intent_classifier.py  # 🎯 意图识别器
│   │       ├── schema_retriever.py   # 🔍 Schema 检索器
│   │       ├── sql_generator.py      # ⚡ SQL 生成器
│   │       ├── sql_executor.py       # 🛡️ SQL 执行器
│   │       └── chat_handler.py       # 💬 闲聊处理器
│   │
│   ├── rag/                       # RAG 模块
│   │   ├── data_loader.py         #   数据加载器
│   │   ├── embeddings.py          #   Embedding 模型
│   │   ├── vector_store.py        #   FAISS 向量存储
│   │   ├── sql_retriever.py       #   SQL 示例检索器
│   │   ├── sql_generator_auto.py  #   自动生成 SQL 示例
│   │   └── feedback_loop.py       #   反馈循环
│   │
│   └── graph/                     # 工作流图
│       └── workflow.py            #   LangGraph 流程定义
│
├── data/                          # 数据目录
│   └── sql_examples/              #   SQL 示例数据
│       ├── base_examples.json     #     基础示例集
│       └── faiss_index/           #     FAISS 索引文件
│
├── docker/                        # Docker 配置
│   ├── Dockerfile                 #   MySQL 镜像构建
│   ├── docker-compose.yml         #   容器编排
│   ├── my.cnf                     #   MySQL 配置
│   └── init/                      #   初始化 SQL 脚本
│
└── scripts/                       # 工具脚本
    ├── init_rag.py                #   RAG 索引初始化
    └── start_vllm.sh              #   vLLM 模型部署脚本
```

---

## 🚀 快速开始

### 1️⃣ 克隆项目

```bash
git clone https://github.com/TaoJiang999/SQL-Agent.git
cd SQL-Agent
```

---

### 2️⃣ 环境准备

#### 2.1 安装 Docker

本项目需要 Docker 来运行 MySQL 沙箱容器。

- **Windows**: 下载安装 [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- **macOS**: `brew install --cask docker`
- **Linux (Ubuntu)**:
  ```bash
  sudo apt-get update
  sudo apt-get install docker.io docker-compose
  sudo systemctl start docker
  sudo systemctl enable docker
  ```

安装完成后验证：
```bash
docker --version
docker-compose --version
```

#### 2.2 构建 Python 环境 (uv)

推荐使用 [uv](https://docs.astral.sh/uv/) 作为 Python 包管理器：

```bash
# 安装 uv
pip install uv

# 创建虚拟环境并安装依赖
uv venv --python 3.11
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

# 安装项目依赖
uv pip install -e .

# (可选) 安装开发依赖
uv pip install -e ".[dev]"
```

#### 2.3 构建 MySQL 容器

启动 Docker MySQL 沙箱（包含电商数据库 schema 和示例数据）：

```bash
cd docker
docker-compose up -d
cd ..
```

验证容器运行状态：
```bash
docker ps
# 应看到 sql-agent-sandbox 容器正在运行

# 测试数据库连接
docker exec -it sql-agent-sandbox mysql -usandbox_user -psandbox_password -e "SHOW DATABASES;"
```

#### 2.4 构建 RAG 索引

初始化 FAISS 向量索引，加载 SQL 示例数据用于 RAG 检索增强：

```bash
python scripts/init_rag.py init
```

验证索引状态：
```bash
python scripts/init_rag.py status
```

---

### 3️⃣ 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env
```

编辑 `.env` 文件，根据你的模型部署方式选择配置：

#### 方式 A：使用云端 API 提供商

适用于使用 OpenAI、Google Gemini 或其他兼容 OpenAI 格式的 API 服务：

```env
# LangChain 追踪 (可选，用于调试)
LANGCHAIN_API_KEY=your_langchain_api_key
LANGCHAIN_TRACING_V2=true

# 模型配置 —— 选择你的 API 提供商
MODEL_NAME=gpt-4o                  # 或 gemini-2.5-flash 等
MODEL_PROVIDER=openai              # 或 google_genai
MODEL_BASE_URL=https://api.openai.com/v1   # API 地址
MODEL_API_KEY=sk-your_api_key      # 你的 API Key
```

常见 API 提供商配置示例：

| 提供商 | MODEL_NAME | MODEL_PROVIDER | MODEL_BASE_URL |
|--------|-----------|----------------|----------------|
| OpenAI | `gpt-4o` | `openai` | `https://api.openai.com/v1` |
| Google | `gemini-2.5-flash` | `google_genai` | `https://generativelanguage.googleapis.com` |
| 第三方代理 | `gpt-4o` | `openai` | `https://your-proxy.com/v1` |

#### 方式 B：使用 vLLM 本地部署

适用于有 GPU 服务器，希望本地部署开源模型（如 Qwen2.5）的场景：

**① 启动 vLLM 服务：**

```bash
# 修改脚本中的 MODEL_PATH 为你的模型路径
# 可根据需要调整 GPU 数量、量化方式等参数
bash scripts/start_vllm.sh
```

主要可配置参数：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `MODEL_PATH` | (需修改) | HuggingFace 模型本地路径 |
| `CUDA_DEVICES` | `0,1` | 使用的 GPU 编号 |
| `QUANTIZATION` | `gptq_marlin` | 量化方式 |
| `TENSOR_PARALLEL_SIZE` | `2` | 张量并行数 (= GPU 数量) |
| `MAX_MODEL_LEN` | `32768` | 最大上下文长度 |

**② 配置 `.env` 文件：**

```env
MODEL_NAME=qwen-agent               # vLLM served-model-name
MODEL_PROVIDER=openai                # vLLM 兼容 OpenAI 格式
MODEL_BASE_URL=http://localhost:8000/v1
MODEL_API_KEY=not-needed             # 本地部署无需 API Key
```

---

### 4️⃣ 启动项目

#### 方式一：使用 LangGraph Dev Server（推荐）

```bash
langgraph dev
```

启动后访问 [http://localhost:8123](http://localhost:8123) 打开 LangGraph Studio 进行可视化调试。

#### 方式二：使用 Python 直接运行

```python
import asyncio
from src.graph.workflow import run_sql_agent

async def main():
    result = await run_sql_agent("查询销量最高的10个商品")
    print(f"意图: {result['intent']}")
    print(f"SQL:  {result['sql']}")
    print(f"结果: {result['result']}")

asyncio.run(main())
```

---

### 5️⃣ 使用演示

以下是一些示例查询：

```
💬 闲聊示例:
  > 你好，你能做什么？

📊 SQL 查询示例:
  > 查询销量最高的10个商品
  > 统计每个分类的商品数量
  > 查询过去7天的订单总额
  > 查询没有下过单的用户
```

**Agent 处理流程：**

```
用户: "查询销量最高的10个商品"
  │
  ├─ 🎯 Intent Classifier  →  识别为 text_to_sql 意图
  ├─ 🔍 Schema Retriever   →  定位 products, order_items 表
  ├─ ⚡ SQL Generator       →  生成 SELECT ... ORDER BY ... LIMIT 10
  ├─ 🛡️ SQL Executor        →  在安全沙箱中执行 SQL
  │
  └─ ✅ 返回查询结果 + SQL 解释
```

---

## 📄 License

MIT
