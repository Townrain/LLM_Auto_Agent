# 故障排除指南

## 问题：输入问题后没有输出

### 可能的原因和解决方案

#### 1. API Key 配置问题

**症状**: 程序启动后显示 "=== ReAct Agent 启动 ===" 和 "Question:" 提示符，但输入问题后没有响应

**检查步骤**:
1. 运行调试版本：
   ```bash
   python run_agent_debug.py
   ```

2. 如果显示 "❌ 错误: 未找到 DeepSeek API Key"，说明 .env 文件配置有问题

**解决方案**:
- 确保已创建 `.env` 文件（不是 `.env.example`）
- 确保 `.env` 文件与 `run_agent.py` 在同一目录
- 确保 `.env` 文件内容正确：
  ```
  DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
  ```

#### 2. 网络连接问题

**症状**: API Key 配置正确，但仍然没有响应

**检查步骤**:
- 确保网络连接正常
- 确保可以访问 DeepSeek API (https://api.deepseek.com)

#### 3. API Key 无效

**症状**: API Key 配置正确，但 API 调用失败

**检查步骤**:
- 确认 API Key 是否正确
- 确认 API Key 是否有足够的额度
- 确认 API Key 是否已启用

#### 4. 依赖包问题

**症状**: 导入错误或模块未找到

**解决方案**:
```bash
pip install -r requirements.txt
```

### 快速诊断

1. **运行调试版本**：
   ```bash
   python run_agent_debug.py
   ```
   这会显示详细的配置信息

2. **检查 .env 文件**：
   - 确保文件名是 `.env`（不是 `.env.example`）
   - 确保文件内容格式正确
   - 确保文件在正确目录

3. **手动测试 API**：
   ```python
   import requests
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   api_key = os.getenv("DEEPSEEK_API_KEY")
   
   headers = {
       "Authorization": f"Bearer {api_key}",
       "Content-Type": "application/json"
   }
   
   payload = {
       "model": "deepseek-chat",
       "messages": [{"role": "user", "content": "Hello"}],
       "stream": False
   }
   
   response = requests.post(
       "https://api.deepseek.com/chat/completions",
       headers=headers,
       json=payload,
       timeout=30
   )
   
   print(f"状态码: {response.status_code}")
   print(f"响应: {response.text}")
   ```

### 常见错误信息

- **"未找到 DeepSeek API Key"**: .env 文件配置问题
- **"API调用失败: 401"**: API Key 无效
- **"API调用失败: 429"**: 请求频率过高
- **"连接超时"**: 网络问题

### 如果问题仍然存在

1. 在 GitHub Issues 中报告问题
2. 提供以下信息：
   - 操作系统版本
   - Python 版本
   - 错误日志
   - 运行 `python run_agent_debug.py` 的输出