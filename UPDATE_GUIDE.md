# LLM Auto Agent 更新指南 v2.0

## 概述

本项目已进行全面优化和增强，保留了所有现有功能的同时，添加了多项新特性。所有更改都是**向后兼容**的，您的现有代码无需修改即可继续运行。

## 主要增强功能

### 1. 多LLM提供商支持 🚀

**新增功能：**
- ✅ 支持 **DeepSeek**（默认）
- ✅ 支持 **OpenAI** (GPT-4, GPT-4o, GPT-3.5)
- ✅ 支持 **Anthropic** (Claude 3.5 Sonnet, Claude 3.5 Haiku)
- ✅ 智能提供商自动识别
- ✅ API成本估算

**用法：**
```python
# 使用环境变量切换提供商
export LLM_PROVIDER=openai  # 或 deepseek, anthropic
export OPENAI_API_KEY=sk-...

# 或在代码中指定
from config_manager import ConfigManager
config = ConfigManager()
config.set('api.default_provider', 'openai')
```

### 2. 增强的配置管理 ⚙️

**新增功能：**
- ✅ 支持 YAML/JSON 配置文件
- ✅ 环境变量覆盖配置
- ✅ 多层配置结构（API、数据库、日志、安全等）
- ✅ 配置验证和缺省值
- ✅ 完全向后兼容旧版 AgentConfig

**用法：**
```python
# 方式1: 使用新的 ConfigManager
from config_manager import ConfigManager
config = ConfigManager('config.yaml')

# 方式2: 继续使用旧的 AgentConfig
from AgentConfig import AgentConfig
config = AgentConfig()  # 仍然可用！

# 方式3: 环境变量配置
export DEEPSEEK_API_KEY=sk-...
export LLM_PROVIDER=deepseek
export MAX_STEPS=20
export LOG_LEVEL=INFO
```

**创建配置文件 (config.yaml):**
```yaml
api:
  default_provider: "deepseek"
  deepseek:
    api_key: "sk-..."
    base_url: "https://api.deepseek.com"
    default_model: "deepseek-chat"

max_steps: 20
timeout: 60

logging:
  level: "INFO"
  file: "agent.log"
```

### 3. 专业日志系统 📝

**新增功能：**
- ✅ 彩色日志输出（终端）
- ✅ 日志文件轮转
- ✅ 结构化日志（JSON格式）
- ✅ API调用日志
- ✅ 工具调用日志
- ✅ 性能监控
- ✅ 错误计数和统计

**用法：**
```python
from logger import logger

logger.info("普通信息")
logger.warning("警告信息")
logger.error("错误信息", exc_info=True)
logger.debug("调试信息")

# API调用日志
logger.log_api_call("deepseek", "deepseek-chat", 100, 200, 0.001)

# 工具调用日志
logger.log_tool_call("search_web", {"query": "test"}, True, 1.5)
```

**环境变量控制：**
```bash
export LOG_LEVEL=DEBUG      # DEBUG, INFO, WARNING, ERROR
export LOG_FILE=agent.log   # 日志文件路径
export LOG_CONVERSATION=true # 记录对话内容
```

### 4. 智能重试和错误处理 🔄

**新增功能：**
- ✅ 自动重试失败请求（指数退避）
- ✅ 请求超时控制
- ✅ 错误计数和限制
- ✅ 优雅降级
- ✅ 详细的错误信息

**用法：**
```python
# 自动重试配置
export RETRY_ATTEMPTS=3     # 重试次数
export RETRY_DELAY=1        # 重试延迟（秒）
export TIMEOUT=60          # 请求超时（秒）
```

**错误处理示例：**
```python
# 在 agent.py 中自动处理
agent = ReactAgent()
result = agent.run("你的问题")  # 自动重试失败请求

# 获取统计信息
stats = agent.get_stats()
print(f"成功率: {stats['success_rate']}%")
print(f"错误数: {stats['errors']}")
```

### 5. 性能监控和统计 📊

**新增功能：**
- ✅ 执行时间统计
- ✅ API调用次数
- ✅ Token使用量
- ✅ 成本估算
- ✅ 成功率统计
- ✅ 步骤计数

**用法：**
```python
agent = ReactAgent()
result = agent.run("计算 15 * 23")

# 获取详细统计
stats = agent.get_stats()
print(f"执行时间: {stats['elapsed_time']:.1f}秒")
print(f"执行步骤: {stats['steps']}")
print(f"API调用: {stats['api_calls']}")
print(f"Token总数: {stats['total_tokens']}")
print(f"预估成本: ${stats['total_cost']:.6f}")
print(f"成功率: {stats['success_rate']}%")

# API管理器统计
api_stats = agent.api_manager.get_stats()
print(json.dumps(api_stats, indent=2))
```

### 6. 流式响应支持 🔥

**新增功能：**
- ✅ 实时流式输出
- ✅ 逐字显示AI思考过程
- ✅ 更好的用户体验

**用法：**
```python
agent = ReactAgent()

# 使用流式模式
for chunk in agent.run_stream("用Python编写一个快速排序算法"):
    print(chunk, end='', flush=True)
```

### 7. 增强的安全性 🔒

**新增功能：**
- ✅ 命令白名单/黑名单
- ✅ 沙箱模式
- ✅ 代码执行控制
- ✅ 命令长度限制

**配置安全选项：**
```yaml
security:
  enable_sandbox: true
  allowed_commands: ["ls", "pwd", "cat", "python", "python3"]
  blocked_commands: ["rm -rf", "dd", "shutdown", "reboot"]
  max_command_length: 1000
  enable_code_execution: true
```

### 8. 工具系统增强 🔧

**新增功能：**
- ✅ Web搜索
- ✅ Python代码执行
- ✅ 文件操作
- ✅ Shell命令
- ✅ 数学计算
- ✅ 数据库操作（可选）

**配置工具选项：**
```yaml
tools:
  enable_web_search: true
  enable_file_operations: true
  search_timeout: 10
  file_size_limit: 10485760  # 10MB
```

## 向后兼容性

### ✅ 完全兼容旧代码

所有现有代码无需修改即可运行：

```python
# 旧代码（仍然完全可用）
from AgentConfig import AgentConfig
from agent import ReactAgent

config = AgentConfig()
agent = ReactAgent(config)
result = agent.run("计算 15 * 23")

# 新代码（推荐使用）
from config_manager import ConfigManager
from agent import ReactAgent

config = ConfigManager()
agent = ReactAgent(config)
result = agent.run("计算 15 * 23")
```

### ✅ 环境变量兼容

所有旧的环境变量仍然有效：
- `DEEPSEEK_API_KEY`
- `DEEPSEEK_BASE_URL`
- `DEEPSEEK_MODEL`
- `DATABASE_CONFIG`（JSON格式）

### ✅ 配置文件兼容

如果已经有 `.env` 文件或数据库配置，它们将继续工作。

## 迁移指南

### 从旧版本迁移到新版本

**步骤1: 安装新依赖**
```bash
pip install -r requirements.txt
```

**步骤2: （可选）创建配置文件**
```bash
# 复制示例配置（可选）
cp config_example.yaml config.yaml

# 编辑配置文件
nano config.yaml
```

**步骤3: 更新环境变量（推荐）**
```bash
# 在 .env 文件中添加
LLM_PROVIDER=deepseek
LOG_LEVEL=INFO
TIMEOUT=60
MAX_STEPS=20
```

**步骤4: 测试运行**
```bash
python run_agent.py
```

### 推荐的代码更新

虽然不是必须的，但推荐更新代码以使用新功能：

**旧代码:**
```python
from AgentConfig import AgentConfig
from agent import ReactAgent

config = AgentConfig()
agent = ReactAgent(config)
result = agent.run("你的问题")
```

**新代码:**
```python
from config_manager import ConfigManager
from agent import ReactAgent

# 使用新的配置管理器
config = ConfigManager('config.yaml')  # 可选：加载配置文件
agent = ReactAgent(config)

# 使用流式输出
for chunk in agent.run_stream("你的问题"):
    print(chunk, end='', flush=True)

# 查看统计
stats = agent.get_stats()
print(f"\n成本: ${stats['total_cost']:.6f}")
```

## 故障排除

### 问题1: 导入错误
```
ImportError: No module named 'config_manager'
```
**解决:** 确保所有新文件已下载：
```bash
git pull origin main
```

### 问题2: API密钥错误
```
Error: DeepSeek API key not found
```
**解决:** 设置API密钥：
```bash
export DEEPSEEK_API_KEY=sk-...
```

### 问题3: 依赖安装失败
```
ERROR: Could not install packages...
```
**解决:** 使用虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 问题4: 旧代码不工作

如果旧代码出现问题，可以使用兼容模式：
```python
# 使用旧的导入方式
import sys
sys.path.insert(0, '.')

from AgentConfig import AgentConfig
from agent import ReactAgent

# 确保环境变量已设置
import os
os.environ['DEEPSEEK_API_KEY'] = 'sk-...'

config = AgentConfig()
agent = ReactAgent(config)
result = agent.run("测试问题")
```

## 性能优化建议

### 1. 调整重试策略
```yaml
# config.yaml
retry_attempts: 3      # 减少重试次数以提高速度
retry_delay: 1         # 减少重试延迟
timeout: 30           # 减少超时时间
```

### 2. 限制工具使用
```yaml
# config.yaml
security:
  enable_code_execution: false  # 禁用代码执行以提高安全性

tools:
  enable_web_search: false      # 禁用网页搜索以提高速度
```

### 3. 调整对话历史
```yaml
# config.yaml
conversation:
  max_history: 5        # 减少历史消息数以节省token
  context_window: 4000  # 限制上下文窗口
```

## 新功能示例

### 示例1: 多LLM切换
```python
from config_manager import ConfigManager
from agent import ReactAgent

# 使用 OpenAI
config = ConfigManager()
config.set('api.default_provider', 'openai')
config.set('api.openai.api_key', 'sk-...')

agent = ReactAgent(config)
result = agent.run("用Python编写一个类来计算圆的面积")
```

### 示例2: 流式输出
```python
agent = ReactAgent()

print("AI正在思考...\n")
for chunk in agent.run_stream("解释量子计算的基本原理"):
    print(chunk, end='', flush=True)

print("\n\n完成！")
```

### 示例3: 查看详细统计
```python
agent = ReactAgent()

# 运行任务
result = agent.run("北京今天的天气怎么样？")

# 获取统计
stats = agent.get_stats()
print(f"\\n执行统计:")
print(f"  时间: {stats['elapsed_time']:.1f}s")
print(f"  Token: {stats['total_tokens']}")
print(f"  成本: ${stats['total_cost']:.6f}")

# API提供商统计
for provider, p_stats in stats['api_stats']['by_provider'].items():
    print(f"  {provider}: {p_stats['request_count']}次调用, "
          f"${p_stats['total_cost']:.6f}")
```

### 示例4: 错误处理
```python
from logger import error_counter

agent = ReactAgent()

# 重置错误计数器
error_counter.reset()

# 运行任务
result = agent.run("可能会导致错误的任务")

# 检查错误
if error_counter.should_stop('api_error'):
    print("API错误过多，停止执行")

error_stats = error_counter.get_stats()
print(f"错误统计: {error_stats}")
```

## 版本信息

- **当前版本**: v2.0（增强版）
- **发布日期**: 2024-11-22
- **兼容性**: 完全向后兼容 v1.x
- **主要变更**: 
  - 新增多LLM支持
  - 增强配置管理
  - 专业日志系统
  - 智能重试机制
  - 性能监控

## 支持和反馈

如有问题或建议，请：
1. 查看 TROUBLESHOOTING.md
2. 创建 GitHub Issue
3. 查看日志文件: `agent.log`

## 许可证

本项目继续使用 MIT 许可证。所有增强功能都遵循相同的许可证条款。
