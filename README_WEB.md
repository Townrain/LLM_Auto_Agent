# LLM Auto Agent Web 界面

基于 Flask 的现代化 Web 交互界面，为 LLM Auto Agent 提供友好的用户界面。

## ✨ 功能特性

### 🎯 核心功能
- **智能对话** - 基于 DeepSeek API 的智能对话
- **多会话管理** - 支持创建、切换、删除多个对话
- **历史记录** - 完整的对话历史管理
- **实时响应** - 流畅的实时消息显示

### ⚙️ 配置管理
- **API 配置** - 用户可自行添加 DeepSeek API Key
- **数据库选项** - 可选择是否启用数据库功能
- **知识库导入** - 支持多种格式文件上传

### 🛡️ 安全特性
- **命令确认** - 系统命令执行前弹窗确认
- **错误处理** - 完善的错误提示和用户引导
- **会话管理** - 自动清理过期会话

## 🚀 快速开始

### 1. 安装依赖
```bash
# 安装核心依赖
pip install -r requirements.txt

# 安装 Web 应用依赖
pip install -r web_requirements.txt
```

### 2. 配置环境变量
创建 `.env` 文件（可选）：
```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
USE_DATABASE=false
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=llm_agent
```

### 3. 启动 Web 应用
```bash
python web_app.py
```

### 4. 访问界面
打开浏览器访问：`http://127.0.0.1:5000`

## 📖 使用指南

### 首次使用
1. 点击左下角 **"设置"** 按钮
2. 配置您的 **DeepSeek API Key**
3. 选择是否启用数据库功能
4. 点击 **"保存设置"**

### 开始对话
1. 在底部输入框输入您的问题
2. 按 **Enter** 发送消息
3. 查看 AI 助手的实时回复

### 管理对话
- **新建对话**：点击 **"+ 新对话"** 按钮
- **切换对话**：点击侧边栏的对话标题
- **删除对话**：点击对话旁边的 **🗑️** 按钮
- **清空所有**：点击 **"🗑️ 清空所有对话"**

### 导入知识库
1. 点击 **"导入"** 按钮
2. 选择要上传的文件（支持 TXT、PDF、DOC、DOCX、Markdown 等格式）
3. 等待上传完成

## 🔧 故障排除

### 常见问题

#### 1. "ReactAgent.run() takes 1 positional argument but 2 were given"
**问题原因**：参数传递错误
**解决方案**：已修复，确保在初始化时传入用户输入

#### 2. "无法初始化 AI 助手"
**可能原因**：
- API Key 未配置或无效
- 网络连接问题
- Agent 模块导入失败

**解决方案**：
- 检查 API Key 配置
- 确认网络连接正常
- 验证依赖安装完整

#### 3. "处理超时"
**可能原因**：
- Agent 处理时间过长
- 服务器资源不足

**解决方案**：
- 简化问题或分步骤提问
- 检查服务器性能

#### 4. 文件上传失败
**可能原因**：
- 文件格式不支持
- 文件大小超过限制（16MB）
- 服务器存储空间不足

**解决方案**：
- 检查文件格式和大小
- 清理服务器存储空间

### 调试模式
如需启用详细日志，修改 `web_app.py`：
```python
logging.basicConfig(
    level=logging.DEBUG,  # 改为 DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## 📁 文件结构

```
LLM_Auto_Agent/
├── web_app.py              # Flask 后端服务器
├── templates/
│   └── index.html          # 主界面模板
├── static/
│   ├── css/
│   │   └── style.css       # 样式文件
│   └── js/
│       └── app.js          # 前端逻辑
├── web_requirements.txt    # Web 应用依赖
└── README_WEB.md          # 本文档
```

## 🎨 界面特色

- **现代化设计** - 类似 ChatGPT 的聊天界面
- **响应式布局** - 支持桌面端和移动端
- **实时交互** - 流畅的消息发送和接收
- **直观操作** - 清晰的按钮和提示

## 🔄 更新日志

### 最新修复
- ✅ 修复 ReactAgent.run() 参数传递错误
- ✅ 添加历史对话删除功能
- ✅ 改进 AI 回复显示
- ✅ 优化错误处理和用户提示

### 功能完善
- ✅ 完整的对话管理（创建、删除、切换）
- ✅ 实时消息显示和格式化
- ✅ 系统命令安全确认
- ✅ 文件上传和知识库导入

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个 Web 界面！

## 📄 许可证

本项目基于 MIT 许可证开源。