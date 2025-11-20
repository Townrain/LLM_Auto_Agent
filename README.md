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

## 🛠️ 系统架构

### 核心组件

- `agent.py` - 主要的 ReAct Agent 类
- `AgentConfig.py` - 配置管理类
- `ConversationManager.py` - 对话管理类
- `Toolmanager.py` - 工具管理类
- `agent_tools.py` - 工具函数集合
- `run_agent.py` - 运行入口

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
```

## 📖 详细文档

- [设置指南](SETUP_GUIDE.md) - 详细的安装和配置说明
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