# LLM Auto Agent

一个基于 ReAct（Reasoning and Acting）模式的智能代理系统，支持 DeepSeek API。

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/Townrain/LLM_Auto_Agent.git
cd LLM_Auto_Agent
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置 DeepSeek API Key

**方法一：创建 .env 文件**
```bash
# 复制示例文件
cp .env.example .env
# 编辑 .env 文件，添加您的 API Key
```

**方法二：设置环境变量**
```bash
# Windows
set DEEPSEEK_API_KEY=your_api_key_here

# Linux/Mac
export DEEPSEEK_API_KEY=your_api_key_here
```

### 4. 运行程序
```bash
python run_agent.py
```

> **注意**：首次使用请先获取 [DeepSeek API Key](https://platform.deepseek.com/)

## 📋 项目特性

- 🤖 **智能推理**: 基于 DeepSeek 模型的智能对话和推理能力
- 🔧 **多工具集成**: 支持文件操作、网页搜索、系统命令执行等多种工具
- 💬 **对话管理**: 智能的上下文管理和对话状态维护
- 🔄 **自动循环**: 支持多步推理和工具调用的自动化流程
- ⚙️ **灵活配置**: 可配置的参数和环境设置
- 🗄️ **可选数据库**: 支持 MySQL 数据库集成，提供长期记忆和个性化服务

## 🛠️ 系统架构

### 核心组件

- `agent.py` - 主要的 ReAct Agent 类
- `AgentConfig.py` - 配置管理类
- `ConversationManager.py` - 对话管理类
- `Toolmanager.py` - 工具管理类
- `agent_tools.py` - 工具函数集合
- `run_agent.py` - 运行入口

### 数据库组件（可选）

- `database_tools.py` - 数据库管理类
- `database_agent_tools.py` - 数据库工具函数集

### 工作流程

1. **用户输入** → 接收用户问题
2. **推理阶段** → AI 分析问题并制定行动计划
3. **行动阶段** → 执行相应的工具调用
4. **观察阶段** → 获取工具执行结果
5. **循环或结束** → 根据结果决定继续推理或给出最终答案

## 🔧 主要工具功能

### 文件操作
- `read_file()`: 读取文件内容
- `write_to_file()`: 写入文件内容

### 系统命令
- `run_terminal_command()`: 执行系统终端命令（含安全确认机制）

### 网页搜索
- `search_web()`: 使用 DuckDuckGo 搜索网络内容
- `fetch_webpage_content()`: 获取网页内容并提取主要文本
- `search_and_summarize()`: 搜索网络内容并获取详细信息

### Python 代码执行
- `create_and_run_python_file()`: 创建 Python 文件并在指定 conda 环境中执行

### 数据库工具（可选）
- `search_database_context()`: 从数据库搜索相关上下文信息
- `search_knowledge_base()`: 从知识库搜索相关信息
- `log_conversation()`: 将对话记录保存到数据库
- `get_user_conversation_history()`: 获取用户对话历史

## ⚙️ 配置说明

### AgentConfig 配置参数

```python
# API配置
api_key = "your_deepseek_api_key"  # DeepSeek API Key
model_name = "deepseek-chat"       # 模型名称
base_url = "https://api.deepseek.com"  # API 地址

# 对话管理
max_steps = 10                     # 最大推理步数
refresh_prompt_interval = 3        # 提示词刷新间隔

# 调试配置
show_system_messages = False       # 是否显示系统消息
conda = "New"                      # Conda 环境名称

# 数据库配置（可选）
enable_database = False            # 是否启用数据库功能，默认禁用
database_config = {                # 数据库连接配置
    'host': 'localhost',
    'database': 'llm_agent',
    'user': 'your_username',
    'password': 'your_password',
    'port': 3306
}
```

## 🗄️ 数据库功能（可选）

数据库功能默认**禁用**，用户需要明确启用才能使用。

### 启用数据库

**方法一：配置文件**
```python
# 在 AgentConfig.py 中设置
enable_database = True
database_config = {
    'host': 'localhost',
    'database': 'llm_agent',
    'user': 'your_username',
    'password': 'your_password',
    'port': 3306
}
```

**方法二：环境变量**
```bash
export ENABLE_DATABASE=true
export DB_HOST=localhost
export DB_NAME=llm_agent
export DB_USER=root
export DB_PASSWORD=your_password
export DB_PORT=3306
```

### 数据库特性

- ✅ **智能上下文收集**: AI 在回答前自动从数据库获取相关上下文
- ✅ **长期记忆**: 存储对话历史、用户偏好和知识库
- ✅ **个性化服务**: 基于用户历史行为提供定制化回答
- ✅ **知识管理**: 构建可搜索的知识库系统

详细使用说明请参考 [DATABASE_INTEGRATION_GUIDE.md](DATABASE_INTEGRATION_GUIDE.md)

## 📖 详细文档

- [设置指南](SETUP_GUIDE.md) - 详细的安装和配置说明
- [数据库集成指南](DATABASE_INTEGRATION_GUIDE.md) - MySQL 数据库集成说明
- [API 文档](https://platform.deepseek.com/api-docs/) - DeepSeek API 官方文档

## 🐛 问题反馈

如果您遇到任何问题，请：

1. 检查 [SETUP_GUIDE.md](SETUP_GUIDE.md) 中的常见问题解决方案
2. 确保已正确配置 DeepSeek API Key
3. 检查网络连接和依赖安装

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- 原始项目：[LtdEdition-Peng/LLM_Auto_Agent](https://github.com/LtdEdition-Peng/LLM_Auto_Agent)
- DeepSeek API：[DeepSeek 开放平台](https://platform.deepseek.com/)