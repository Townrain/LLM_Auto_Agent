"""
MySQL Database Tools for LLM Auto Agent
Provides database query and management capabilities
"""

import mysql.connector
from mysql.connector import Error
import json
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """MySQL database management class"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize database connection
        
        Args:
            config: Database configuration dictionary
        """
        self.config = config
        self.connection = None
        self.connect()
    
    def connect(self) -> bool:
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.config.get('host', 'localhost'),
                database=self.config.get('database', 'llm_agent'),
                user=self.config.get('user', 'root'),
                password=self.config.get('password', ''),
                port=self.config.get('port', 3306)
            )
            logger.info("Database connection established")
            return True
        except Error as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    def execute_query(self, query: str, params: tuple = None) -> Optional[List[Dict]]:
        """Execute SQL query and return results"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                return results
            else:
                self.connection.commit()
                return None
        except Error as e:
            logger.error(f"Query execution failed: {e}")
            return None
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def close(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("Database connection closed")

class DatabaseTools:
    """Database tools for LLM Agent"""
    
    def __init__(self, db_config: Dict[str, Any]):
        """
        Initialize database tools
        
        Args:
            db_config: Database configuration
        """
        self.db_manager = DatabaseManager(db_config)
        self.initialize_tables()
    
    def initialize_tables(self):
        """Initialize required database tables"""
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
            self.db_manager.execute_query(create_sql)
    
    def search_conversation_history(self, user_id: str, query: str = None, limit: int = 10) -> List[Dict]:
        """Search conversation history for context"""
        if query:
            sql = """
                SELECT user_message, agent_response, timestamp 
                FROM conversation_history 
                WHERE user_id = %s AND (user_message LIKE %s OR agent_response LIKE %s)
                ORDER BY timestamp DESC 
                LIMIT %s
            """
            params = (user_id, f'%{query}%', f'%{query}%', limit)
        else:
            sql = """
                SELECT user_message, agent_response, timestamp 
                FROM conversation_history 
                WHERE user_id = %s 
                ORDER BY timestamp DESC 
                LIMIT %s
            """
            params = (user_id, limit)
        
        return self.db_manager.execute_query(sql, params) or []
    
    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile and preferences"""
        sql = "SELECT * FROM user_profiles WHERE user_id = %s"
        results = self.db_manager.execute_query(sql, (user_id,))
        return results[0] if results else None
    
    def search_knowledge_base(self, query: str, category: str = None, limit: int = 5) -> List[Dict]:
        """Search knowledge base for relevant information"""
        if category:
            sql = """
                SELECT title, content, category, tags 
                FROM knowledge_base 
                WHERE (title LIKE %s OR content LIKE %s) AND category = %s
                ORDER BY id DESC 
                LIMIT %s
            """
            params = (f'%{query}%', f'%{query}%', category, limit)
        else:
            sql = """
                SELECT title, content, category, tags 
                FROM knowledge_base 
                WHERE title LIKE %s OR content LIKE %s
                ORDER BY id DESC 
                LIMIT %s
            """
            params = (f'%{query}%', f'%{query}%', limit)
        
        return self.db_manager.execute_query(sql, params) or []
    
    def log_conversation(self, user_id: str, session_id: str, user_message: str, agent_response: str, metadata: Dict = None):
        """Log conversation to database"""
        sql = """
            INSERT INTO conversation_history (user_id, session_id, user_message, agent_response, metadata)
            VALUES (%s, %s, %s, %s, %s)
        """
        metadata_json = json.dumps(metadata) if metadata else None
        self.db_manager.execute_query(sql, (user_id, session_id, user_message, agent_response, metadata_json))
    
    def log_tool_usage(self, session_id: str, tool_name: str, parameters: Dict, result: str):
        """Log tool usage for analysis"""
        sql = """
            INSERT INTO tool_usage_logs (session_id, tool_name, parameters, result)
            VALUES (%s, %s, %s, %s)
        """
        params_json = json.dumps(parameters) if parameters else None
        self.db_manager.execute_query(sql, (session_id, tool_name, params_json, result))
    
    def get_context_for_query(self, user_id: str, current_query: str) -> Dict[str, Any]:
        """
        Collect relevant context from database before processing query
        This is the main function that AI should call first
        """
        context = {
            'user_profile': None,
            'recent_conversations': [],
            'relevant_knowledge': [],
            'similar_queries': []
        }
        
        # Get user profile
        context['user_profile'] = self.get_user_profile(user_id)
        
        # Search recent conversations for context
        context['recent_conversations'] = self.search_conversation_history(user_id, limit=5)
        
        # Search knowledge base for relevant information
        context['relevant_knowledge'] = self.search_knowledge_base(current_query, limit=3)
        
        # Search for similar past queries
        context['similar_queries'] = self.search_conversation_history(user_id, current_query, limit=3)
        
        return context

# Database tool functions for agent integration
def create_database_tools(db_config: Dict[str, Any]) -> DatabaseTools:
    """Factory function to create database tools"""
    return DatabaseTools(db_config)