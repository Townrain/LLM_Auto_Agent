"""
Database Configuration Example
Copy this file to database_config.py and modify with your actual database settings
"""

# Database Configuration
DATABASE_CONFIG = {
    'host': 'localhost',           # Database host
    'database': 'llm_agent',       # Database name
    'user': 'root',                # Database username
    'password': 'your_password',   # Database password
    'port': 3306                   # Database port
}

# Environment variables (alternative configuration method)
# Set these environment variables to override the above settings:
# DB_HOST=localhost
# DB_NAME=llm_agent
# DB_USER=root
# DB_PASSWORD=your_password
# DB_PORT=3306

# Database initialization SQL (run this in your MySQL client)
DATABASE_INIT_SQL = """
-- Create database
CREATE DATABASE IF NOT EXISTS llm_agent;
USE llm_agent;

-- Create conversation history table
CREATE TABLE IF NOT EXISTS conversation_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255),
    session_id VARCHAR(255),
    user_message TEXT,
    agent_response TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata JSON
);

-- Create user profiles table
CREATE TABLE IF NOT EXISTS user_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE,
    preferences JSON,
    context_data JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create knowledge base table
CREATE TABLE IF NOT EXISTS knowledge_base (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(255),
    title VARCHAR(500),
    content TEXT,
    tags JSON,
    source VARCHAR(500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create tool usage logs table
CREATE TABLE IF NOT EXISTS tool_usage_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(255),
    tool_name VARCHAR(255),
    parameters JSON,
    result TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_conversation_user_id ON conversation_history(user_id);
CREATE INDEX idx_conversation_timestamp ON conversation_history(timestamp);
CREATE INDEX idx_knowledge_category ON knowledge_base(category);
CREATE INDEX idx_knowledge_title ON knowledge_base(title);
"""

# Sample data insertion (optional)
SAMPLE_DATA_SQL = """
-- Insert sample user profile
INSERT IGNORE INTO user_profiles (user_id, preferences, context_data) 
VALUES ('default_user', '{\"language\": \"zh-CN\", \"theme\": \"dark\"}', '{\"last_project\": \"LLM Agent\"}');

-- Insert sample knowledge base entries
INSERT IGNORE INTO knowledge_base (category, title, content, tags, source) VALUES
('AI', 'ReAct Pattern', 'ReAct (Reasoning and Acting) is a framework that combines reasoning traces and task-specific actions in an interleaved manner.', '["AI", "Reasoning", "Acting"]', 'Research Paper'),
('Programming', 'Python Decorators', 'Decorators are a powerful tool in Python that allow you to modify the behavior of functions or classes.', '["Python", "Programming", "Decorators"]', 'Python Documentation'),
('Database', 'MySQL Indexing', 'Proper indexing can significantly improve query performance in MySQL databases.', '["MySQL", "Database", "Performance"]', 'MySQL Best Practices');
"""

if __name__ == "__main__":
    print("Database Configuration Example")
    print("=" * 50)
    print("1. Copy this file to database_config.py")
    print("2. Modify the DATABASE_CONFIG with your actual database settings")
    print("3. Run the SQL statements in your MySQL client to initialize the database")
    print("4. Set environment variables if using that method")
    print("=" * 50)
    print("\nDatabase Configuration:")
    for key, value in DATABASE_CONFIG.items():
        print(f"  {key}: {value}")