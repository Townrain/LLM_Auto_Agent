# LLM Auto Agent Web 界面

基于 Flask 的 Web 交互界面，为 LLM Auto Agent 提供现代化的用户界面。

## 🌟 功能特性

### ✅ 核心功能
- **API Key 配置**：用户可自行添加 DeepSeek API Key
- **数据库管理**：可选择是否启用数据库功能
- **对话管理**：创建新对话、查看历史记录
- **知识库导入**：支持多种文件格式的知识库导入
- **系统命令确认**：执行系统命令时弹窗确认

### 🎨 界面特色
- **现代化设计**：类似 ChatGPT 的聊天界面
- **响应式布局**：支持桌面端和移动端
- **实时交互**：流畅的消息发送和接收
- **推理过程展示**：显示 AI 的思考步骤和工具使用情况

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装 Web 界面依赖
pip install -r web_requirements.txt

# 或者安装所有依赖（包括原有项目依赖）
pip install -r requirements.txt
pip install -r web_requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件（可选，也可以在 Web 界面中配置）：

```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
USE_DATABASE=false
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=llm_agent
```

### 3. 启动 Web 服务

```bash
python web_app.py
```

### 4. 访问 Web 界面

打开浏览器访问：`http://localhost:5000`

## 📋 使用指南

### 首次使用

1. **配置 API Key**
   - 点击左下角"设置"按钮
   - 输入您的 DeepSeek API Key
   - 选择是否启用数据库功能
   - 保存设置

2. **开始对话**
   - 在输入框中输入问题
   - 按 Enter 发送消息
   - 使用 Shift+Enter 换行

### 对话管理

- **新对话**：点击侧边栏的"新对话"按钮
- **历史记录**：点击顶部导航的"历史记录"按钮
- **切换对话**：在侧边栏点击不同的对话记录

### 知识库管理

- **导入知识库**：点击顶部导航的"导入"按钮
- **支持格式**：TXT, PDF, DOC, DOCX, Markdown
- **使用知识库**：Agent 会自动从导入的知识库中检索相关信息

### 系统命令确认

当 Agent 需要执行系统命令时，会自动弹出确认对话框：

- **查看命令**：确认前查看要执行的命令
- **安全警告**：系统会显示安全警告提示
- **确认执行**：只有用户确认后才会执行命令

## 🛠️ 技术架构

### 后端 (Flask)
- **web_app.py**：主服务器文件
- **API 接口**：
  - `/api/initialize` - 初始化 Agent
  - `/api/chat` - 处理聊天请求
  - `/api/history` - 获取历史记录
  - `/api/new_conversation` - 创建新对话
  - `/api/import_knowledge` - 导入知识库
  - `/api/confirm_command` - 确认系统命令

### 前端 (HTML/CSS/JavaScript)
- **templates/index.html**：主界面模板
- **static/css/style.css**：样式文件
- **static/js/app.js**：前端逻辑

### 数据存储
- **SQLite**：用于 Web 界面会话管理
- **MySQL**：可选，用于 Agent 的数据库功能

## 🔧 配置选项

### API 配置
- **DeepSeek API Key**：必需，用于调用 DeepSeek 模型
- **模型选择**：支持 DeepSeek 系列模型

### 数据库配置
- **启用/禁用**：可选择是否使用数据库
- **连接参数**：主机、端口、用户名、密码、数据库名
- **功能**：对话历史、用户个性化、知识库存储

### 界面配置
- **主题**：支持浅色/深色主题（计划中）
- **语言**：中英文界面（计划中）
- **快捷键**：自定义快捷键（计划中）

## 🐛 故障排除

### 常见问题

1. **API Key 错误**
   - 检查 API Key 是否正确
   - 确认 API Key 有足够的额度
   - 检查网络连接

2. **数据库连接失败**
   - 检查数据库服务是否运行
   - 确认连接参数正确
   - 检查防火墙设置

3. **界面加载失败**
   - 检查端口 5000 是否被占用
   - 清除浏览器缓存
   - 检查控制台错误信息

### 日志查看

```bash
# 查看 Flask 日志
tail -f logs/web_app.log

# 查看 Agent 日志
tail -f logs/agent.log
```

## 🔄 开发说明

### 项目结构
```
LLM_Auto_Agent/
├── web_app.py              # Web 服务器
├── templates/
│   └── index.html          # 主界面模板
├── static/
│   ├── css/
│   │   └── style.css       # 样式文件
│   └── js/
│       └── app.js          # 前端逻辑
├── web_requirements.txt    # Web 依赖
└── README_WEB.md          # 本文档
```

### 扩展开发

1. **添加新工具**：在 `agent_tools.py` 中添加工具函数
2. **修改界面**：编辑对应的 HTML/CSS/JS 文件
3. **添加 API**：在 `web_app.py` 中添加新的路由
4. **自定义样式**：修改 `static/css/style.css`

## 📞 支持与反馈

如果您在使用过程中遇到问题或有改进建议：

1. 查看项目文档
2. 提交 Issue
3. 联系开发者

## 📄 许可证

本项目基于 MIT 许可证开源。

---

**享受与 LLM Auto Agent 的智能对话体验！** 🤖✨