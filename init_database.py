#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建数据库和表结构
这是一个可选脚本，只有在需要使用数据库功能时才需要运行
"""

import mysql.connector
from mysql.connector import Error
import os

def create_database_and_tables():
    """创建数据库和表结构"""
    
    # 从环境变量获取数据库配置
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'port': int(os.getenv('DB_PORT', '3306'))
    }
    
    database_name = os.getenv('DB_NAME', 'llm_agent')
    
    try:
        # 连接到MySQL服务器
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        # 创建数据库
        print(f"创建数据库: {database_name}")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
        
        # 使用新创建的数据库
        cursor.execute(f"USE {database_name}")
        
        # 创建表结构
        tables = {
            'conversation_history': """
                CREATE TABLE IF NOT EXISTS conversation_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id VARCHAR(255),
                    session_id VARCHAR(255),
                    user_message TEXT,
                    agent_response TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metadata JSON
                )
            """,
            'user_profiles': """
                CREATE TABLE IF NOT EXISTS user_profiles (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id VARCHAR(255) UNIQUE,
                    preferences JSON,
                    context_data JSON,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """,
            'knowledge_base': """
                CREATE TABLE IF NOT EXISTS knowledge_base (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    category VARCHAR(255),
                    title VARCHAR(500),
                    content TEXT,
                    tags JSON,
                    source VARCHAR(500),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """,
            'tool_usage_logs': """
                CREATE TABLE IF NOT EXISTS tool_usage_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    session_id VARCHAR(255),
                    tool_name VARCHAR(255),
                    parameters JSON,
                    result TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """
        }
        
        for table_name, create_sql in tables.items():
            print(f"创建表: {table_name}")
            cursor.execute(create_sql)
        
        # 创建索引
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_conversation_user_id ON conversation_history(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_conversation_timestamp ON conversation_history(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge_base(category)",
            "CREATE INDEX IF NOT EXISTS idx_knowledge_title ON knowledge_base(title)",
            "CREATE INDEX IF NOT EXISTS idx_tool_usage_session ON tool_usage_logs(session_id)"
        ]
        
        for index_sql in indexes:
            print(f"创建索引: {index_sql.split(' ')[3]}")
            cursor.execute(index_sql)
        
        connection.commit()
        print("数据库初始化完成！")
        
    except Error as e:
        print(f"数据库初始化失败: {e}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()
    
    return True

if __name__ == "__main__":
    print("=== LLM Auto Agent 数据库初始化 ===")
    print("注意：这是一个可选脚本，只有在需要使用数据库功能时才需要运行")
    print()
    
    # 检查数据库依赖
    try:
        import mysql.connector
    except ImportError:
        print("错误：mysql-connector-python 未安装")
        print("请先安装数据库依赖：pip install mysql-connector-python")
        exit(1)
    
    # 检查环境变量
    if not os.getenv('DB_PASSWORD'):
        print("警告：DB_PASSWORD 环境变量未设置")
        print("请确保已设置数据库连接信息")
        print("可以在 .env 文件中设置或直接设置环境变量")
        print()
    
    # 询问用户是否继续
    response = input("是否继续初始化数据库？(y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("取消初始化")
        exit(0)
    
    # 执行初始化
    if create_database_and_tables():
        print("\n数据库初始化成功！")
        print("现在可以运行 LLM Auto Agent 并使用数据库功能了")
    else:
        print("\n数据库初始化失败，请检查配置和连接")
        exit(1)