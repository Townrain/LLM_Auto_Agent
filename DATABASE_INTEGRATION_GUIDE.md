# MySQL 数据库集成指南

本文档介绍如何为 LLM Auto Agent 项目添加 MySQL 数据库工具接口，使 AI 能够从数据库收集资料。

## 🎯 设计目标

通过数据库集成，实现以下功能：

1. **智能上下文收集** - AI 在回答前自动从数据库获取相关上下文
2. **长期记忆** - 存储对话历史、用户偏好和知识库
3. **个性化服务** - 基于用户历史行为提供定制化回答
4. **知识管理** - 构建可搜索的知识库系统

## 📁 新增文件

项目新增了以下文件：

- `database_tools.py` - 核心数据库管理类
- `database_agent_tools.py` - 数据库工具函数集
- `database_config_example.py` - 数据库配置示例
- `DATABASE_INTEGRATION_GUIDE.md` - 本指南

## 🔧 安装依赖

需要安装 MySQL 连接器：

```bash
pip install mysql-connector-python
```

## ⚙️ 可选配置

数据库功能是**完全可选的**，默认情况下**禁用**。用户需要明确启用才能使用数据库功能。

### 启用方式

#### 方式一：配置文件（推荐）

在 `AgentConfig.py` 中设置：

```python
# 启用数据库功能
enable_database = True

# 配置数据库连接
database_config = {
    'host': 'localhost',
    'database': 'llm_agent',
    'user': 'your_username',
    'password': 'your_password',
    'port': 3306
}
```

#### 方式二：环境变量

```bash
# 启用数据库功能
export ENABLE_DATABASE=true

# 配置数据库连接
export DB_HOST=localhost
export DB_NAME=llm_agent
export DB_USER=root
export DB_PASSWORD=your_password
export DB_PORT=3306
```

### 禁用数据库

如果不想使用数据库功能，可以：

1. 不设置任何数据库配置
2. 设置 `enable_database = False`
3. 不安装数据库依赖

系统会在启动时显示数据库状态：
```
[系统] 数据库功能已禁用
```

## 🗄️ 数据库设置

### 1. 创建数据库

运行以下 SQL 语句创建数据库和表：

```sql
-- 创建数据库
CREATE DATABASE IF NOT EXISTS llm_agent;
USE llm_agent;

-- 创建对话历史表
CREATE TABLE IF NOT EXISTS conversation_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255),
    session_id VARCHAR(255),
    user_message TEXT,
    agent_response TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata JSON
);

-- 创建用户资料表
CREATE TABLE IF NOT EXISTS user_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE,
    preferences JSON,
    context_data JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 创建知识库表
CREATE TABLE IF NOT EXISTS knowledge_base (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(255),
    title VARCHAR(500),
    content TEXT,
    tags JSON,
    source VARCHAR(500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建工具使用日志表
CREATE TABLE IF NOT EXISTS tool_usage_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(255),
    tool_name VARCHAR(255),
    parameters JSON,
    result TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 2. 配置数据库连接

复制 `database_config_example.py` 为 `database_config.py` 并修改配置：

```python
# database_config.py
DATABASE_CONFIG = {
    'host': 'localhost',
    'database': 'llm_agent',
    'user': 'your_username',
    'password': 'your_password',
    'port': 3306
}
```

## 🚀 功能特性

### 1. 自动上下文收集

AI 在每次处理用户查询时，会自动：

- 搜索用户的历史对话记录
- 获取用户个人资料和偏好
- 从知识库搜索相关信息
- 查找相似的过往查询

### 2. 数据库工具函数

新增的数据库工具函数：

- `search_database_context(user_id, query)` - 搜索数据库上下文
- `search_knowledge_base(query, category)` - 搜索知识库
- `log_conversation(user_id, session_id, user_message, agent_response)` - 记录对话
- `get_user_conversation_history(user_id)` - 获取用户对话历史
- `add_knowledge_entry(category, title, content)` - 添加知识条目
- `update_user_profile(user_id, preferences)` - 更新用户资料

### 3. 智能提示增强

系统提示词现在包含数据库工具，AI 可以主动使用这些工具来：

- 在回答前收集背景信息
- 基于历史对话提供连贯的回答
- 利用知识库提供准确信息
- 记录重要对话用于后续参考

## 🔍 使用示例

### 场景1：基于历史对话的连贯回答

当用户再次询问类似问题时，AI 会：

1. 自动搜索该用户的历史对话
2. 找到相关的过往问题和回答
3. 提供更准确和连贯的回应

### 场景2：个性化服务

AI 可以：

- 记住用户的偏好设置
- 基于用户过往行为调整回答风格
- 提供个性化的建议和推荐

### 场景3：知识库增强

当用户询问特定主题时，AI 会：

1. 从知识库搜索相关信息
2. 结合知识库内容和实时推理
3. 提供更全面和准确的回答

## 📊 数据库表结构

### conversation_history (对话历史)
- `user_id` - 用户标识
- `session_id` - 会话标识
- `user_message` - 用户消息
- `agent_response` - AI 回复
- `timestamp` - 时间戳
- `metadata` - 额外元数据

### user_profiles (用户资料)
- `user_id` - 用户标识
- `preferences` - 用户偏好设置
- `context_data` - 上下文数据
- `created_at` - 创建时间
- `updated_at` - 更新时间

### knowledge_base (知识库)
- `category` - 分类
- `title` - 标题
- `content` - 内容
- `tags` - 标签
- `source` - 来源

### tool_usage_logs (工具使用日志)
- `session_id` - 会话标识
- `tool_name` - 工具名称
- `parameters` - 参数
- `result` - 执行结果

## 🔒 性能优化

### 索引优化

建议为以下字段创建索引：

```sql
CREATE INDEX idx_conversation_user_id ON conversation_history(user_id);
CREATE INDEX idx_conversation_timestamp ON conversation_history(timestamp);
CREATE INDEX idx_knowledge_category ON knowledge_base(category);
CREATE INDEX idx_knowledge_title ON knowledge_base(title);
```

### 连接池

对于生产环境，建议使用连接池：

```python
import mysql.connector.pooling

# 创建连接池
db_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="llm_pool",
    pool_size=5,
    **DATABASE_CONFIG
)
```

## 🐛 故障排除

### 常见问题

1. **连接失败**
   - 检查数据库服务是否运行
   - 验证用户名和密码
   - 确认网络连接

2. **表不存在**
   - 运行数据库初始化 SQL
   - 检查数据库名称是否正确

3. **权限不足**
   - 确保用户有创建表的权限
   - 检查数据库访问权限

### 调试模式

启用调试信息：

```python
config = AgentConfig()
config.show_system_messages = True
agent = ReactAgent(config)
```

## 📈 扩展建议

### 未来功能

1. **向量搜索** - 集成向量数据库进行语义搜索
2. **缓存机制** - 实现查询结果缓存
3. **数据备份** - 自动备份重要数据
4. **分析仪表板** - 提供使用统计和分析

### 安全考虑

1. **SQL 注入防护** - 使用参数化查询
2. **数据加密** - 敏感数据加密存储
3. **访问控制** - 基于角色的访问控制
4. **审计日志** - 记录所有数据库操作

## 🎉 总结

通过集成 MySQL 数据库，LLM Auto Agent 现在具备了：

- ✅ 智能上下文收集能力
- ✅ 长期记忆机制
- ✅ 个性化服务支持
- ✅ 知识库管理功能
- ✅ 对话历史追踪
- ✅ **可选配置** - 用户完全控制是否启用数据库

这使得 AI 能够提供更准确、更连贯、更个性化的服务，大大提升了用户体验。