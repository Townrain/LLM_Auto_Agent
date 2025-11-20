# LLM Auto Agent Web 界面

基于 [Townrain/LLM_Auto_Agent](https://github.com/Townrain/LLM_Auto_Agent) 的现代化Web交互界面。

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装核心依赖
pip install -r requirements.txt

# 安装Web应用依赖
pip install -r web_requirements.txt
```

### 2. 启动Web应用

**方法一：直接运行**
```bash
python web_app.py
```

**方法二：使用Flask命令**
```bash
# 设置环境变量
export FLASK_APP=web_app.py
export FLASK_ENV=development

# 启动Flask
flask run
```

### 3. 访问界面

打开浏览器访问：**http://127.0.0.1:5000**

## ✅ 启动成功标志

当您看到以下信息时，表示Web应用已成功启动：

```
🚀 启动 LLM Auto Agent Web 界面...
📁 项目路径: /path/to/your/project
🌐 访问地址: http://127.0.0.1:5000
⏹️  按 Ctrl+C 停止服务器
--------------------------------------------------
 * Serving Flask app 'web_app.py'
 * Debug mode: off
 * Running on http://127.0.0.1:5000
```

**注意：** 上面的警告信息 `WARNING: This is a development server...` 是正常的开发环境提醒，不是错误！

## 🎯 功能特性

### ✅ 已实现功能
- **用户API配置** - 自行添加DeepSeek API Key
- **数据库管理** - 可选择是否启用数据库功能
- **知识库导入** - 支持多种文件格式上传
- **对话管理** - 查看历史记录、创建新对话
- **系统命令确认** - 危险命令弹窗确认
- **现代化界面** - 类似ChatGPT的聊天体验

### 🎨 界面特色
- **响应式设计** - 支持桌面端和移动端
- **实时消息** - 流畅的聊天体验
- **本地存储** - 会话状态持久化
- **错误处理** - 完善的用户引导

## 🔧 配置说明

### 首次使用配置

1. **设置API Key**
   - 点击左下角"设置"按钮
   - 输入您的DeepSeek API Key
   - 保存配置

2. **数据库配置（可选）**
   - 启用/禁用数据库功能
   - 配置MySQL连接参数
   - 测试数据库连接

3. **导入知识库**
   - 点击"导入"按钮
   - 选择支持的文件格式
   - 上传并处理文件

## 🛠️ 故障排除

### 常见问题

**1. 端口被占用**
```bash
# 使用不同端口
python web_app.py --port 5001
# 或
flask run --port 5001
```

**2. 依赖安装失败**
```bash
# 更新pip
pip install --upgrade pip

# 重新安装依赖
pip install -r web_requirements.txt --force-reinstall
```

**3. 模块导入错误**
- 确保在项目根目录运行
- 检查requirements.txt是否安装完整
- 验证Python版本（推荐3.8+）

**4. API Key错误**
- 检查DeepSeek API Key是否正确
- 确保API Key有足够的额度
- 验证网络连接

### 日志查看

Web应用会输出详细的日志信息，帮助诊断问题：

```
✅ Agent模块导入成功
🚀 启动 LLM Auto Agent Web 界面...
📁 项目路径: /path/to/project
🌐 访问地址: http://127.0.0.1:5000
```

## 📁 文件结构

```
LLM_Auto_Agent/
├── web_app.py              # Flask后端服务器
├── templates/
│   └── index.html          # 主界面模板
├── static/
│   ├── css/
│   │   └── style.css       # 样式文件
│   └── js/
│       └── app.js          # 前端逻辑
├── web_requirements.txt    # Web依赖
└── README_WEB.md          # 本文件
```

## 🔒 安全提醒

- 不要在公共网络暴露开发服务器
- 生产环境请使用WSGI服务器（如Gunicorn）
- 妥善保管API Key和数据库密码
- 系统命令执行需要用户确认

## 📞 技术支持

如果遇到问题，请：
1. 查看控制台错误信息
2. 检查依赖是否安装完整
3. 验证配置文件是否正确
4. 在GitHub Issues中反馈问题

---

**享受使用 LLM Auto Agent Web 界面！** 🎉