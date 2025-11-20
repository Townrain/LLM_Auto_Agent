# LLM Auto Agent 设置指南

## 快速开始

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

#### 方法一：创建 .env 文件
复制 `.env.example` 文件并重命名为 `.env`，然后编辑：
```bash
cp .env.example .env
```

编辑 `.env` 文件，添加您的 DeepSeek API Key：
```
DEEPSEEK_API_KEY=your_actual_deepseek_api_key_here
```

#### 方法二：设置环境变量
在 Windows 上：
```cmd
set DEEPSEEK_API_KEY=your_actual_deepseek_api_key_here
```

在 Linux/Mac 上：
```bash
export DEEPSEEK_API_KEY=your_actual_deepseek_api_key_here
```

### 4. 获取 DeepSeek API Key
1. 访问 [DeepSeek 开放平台](https://platform.deepseek.com/)
2. 注册账号并登录
3. 在 API Keys 页面创建新的 API Key
4. 复制 API Key 到您的配置中

### 5. 运行程序
```bash
python run_agent.py
```

## 常见问题解决

### 问题1："错误: 未找到 DeepSeek API Key"
**解决方案**：
- 确保已正确设置环境变量或创建了 `.env` 文件
- 检查 `.env` 文件是否在项目根目录
- 确认 API Key 格式正确

### 问题2："ModuleNotFoundError: No module named 'dotenv'"
**解决方案**：
```bash
pip install python-dotenv
```

### 问题3：API 调用超时或失败
**解决方案**：
- 检查网络连接
- 确认 API Key 有效且未过期
- 检查 DeepSeek API 服务状态

### 问题4：程序无响应或卡住
**解决方案**：
- 按 Ctrl+C 中断程序
- 检查 `config.show_system_messages = True` 查看详细日志
- 确保 API Key 配置正确

## 配置说明

### AgentConfig 配置参数
- `api_key`: DeepSeek API Key
- `model_name`: 模型名称（默认：deepseek-chat）
- `base_url`: API 基础地址（默认：https://api.deepseek.com）
- `max_steps`: 最大推理步数（默认：10）
- `show_system_messages`: 是否显示系统消息（默认：False）

### 支持的 DeepSeek 模型
- `deepseek-chat`: 通用对话模型
- `deepseek-coder`: 代码生成模型
- `deepseek-reasoner`: 推理模型

## 使用示例

成功运行后，程序会显示：
```
=== ReAct Agent 启动 ===
Question: 
```

输入您的问题，例如：
```
请帮我创建一个简单的 Python 程序来计算斐波那契数列
```

Agent 将自动推理并执行相应的工具来完成您的请求。