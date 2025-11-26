"""
Database Tools for LLM Agent
Provides database query and management capabilities as agent tools
"""

import mysql.connector
from typing import Dict, Any, List, Optional
import logging
import re

class DatabaseManager:
    """Database connection and management"""
    
    def __init__(self, config):
        self.config = config
        self.connection = None
        self.connect()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.config['host'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password'],
                port=self.config.get('port', 3306)
            )
            logging.info("Database connection established")
        except Exception as e:
            logging.error(f"Database connection failed: {e}")
            raise
    
    def execute_query(self, sql: str, params: tuple = None) -> List[Dict]:
        """Execute SQL query and return results as dictionaries"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(sql, params or ())
            results = cursor.fetchall()
            cursor.close()
            return results
        except Exception as e:
            logging.error(f"Query execution failed: {e}")
            return []
    
    def get_table_schema(self) -> Dict[str, List[str]]:
        """Get all table names and their columns from the database"""
        try:
            cursor = self.connection.cursor()
            
            # Get all table names
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Get columns for each table
            schema = {}
            for table in tables:
                cursor.execute(f"DESCRIBE {table}")
                columns = [row[0] for row in cursor.fetchall()]
                schema[table] = columns
            
            cursor.close()
            return schema
        except Exception as e:
            logging.error(f"Failed to get table schema: {e}")
            return {}
    
    def search_across_tables(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """
        Search across all relevant tables in the database
        Returns results from multiple tables with table context
        """
        schema = self.get_table_schema()
        all_results = {}
        
        # Define search patterns for different table types
        search_patterns = {
            'products': {
                'text_columns': ['name', 'description', 'category', 'village', 'farmer'],
                'display_columns': ['name', 'description', 'price', 'stock', 'category']
            },
            'users': {
                'text_columns': ['username', 'email', 'address'],
                'display_columns': ['username', 'email', 'phone', 'address']
            },
            'knowledge_base': {
                'text_columns': ['title', 'content', 'category', 'tags'],
                'display_columns': ['title', 'content', 'category']
            },
            'orders': {
                'text_columns': ['order_status'],
                'display_columns': ['order_id', 'user_id', 'product_id', 'quantity', 'total_price', 'order_status']
            }
        }
        
        for table_name, patterns in search_patterns.items():
            if table_name not in schema:
                continue
                
            available_columns = schema[table_name]
            text_columns = [col for col in patterns['text_columns'] if col in available_columns]
            display_columns = [col for col in patterns['display_columns'] if col in available_columns]
            
            if not text_columns:
                continue
            
            # Build search conditions
            conditions = []
            params = []
            for column in text_columns:
                conditions.append(f"{column} LIKE %s")
                params.append(f"%{query}%")
            
            where_clause = " OR ".join(conditions)
            
            # Execute query
            sql = f"""
                SELECT {', '.join(display_columns)} 
                FROM {table_name} 
                WHERE {where_clause}
                LIMIT %s
            """
            params.append(limit)
            
            results = self.execute_query(sql, tuple(params))
            if results:
                all_results[table_name] = {
                    'columns': display_columns,
                    'data': results
                }
        
        return all_results
    
    def smart_search(self, query: str, category: str = None, limit: int = 5) -> Dict[str, Any]:
        """
        Smart search that automatically determines the best tables to query
        based on the query content and database schema
        """
        # Analyze query to determine intent
        query_lower = query.lower()
        
        # Product-related queries
        product_keywords = ['价格', '库存', '产品', '商品', '购买', '多少钱', '有货吗', '库存']
        product_brands = ['安吉白茶', '元阳红米', '青城山腊肉', '苗银手镯', '宏村竹笋', '阳朔金桔', '湘西腊鱼', '婺源皇菊']
        
        # User-related queries
        user_keywords = ['用户', '客户', '会员', '地址', '电话', '邮箱']
        
        # Order-related queries
        order_keywords = ['订单', '物流', '支付', '发货', '快递', '收货']
        
        # Determine search focus
        search_focus = 'general'
        
        if any(keyword in query_lower for keyword in product_keywords) or \
           any(brand in query for brand in product_brands):
            search_focus = 'products'
        elif any(keyword in query_lower for keyword in user_keywords):
            search_focus = 'users'
        elif any(keyword in query_lower for keyword in order_keywords):
            search_focus = 'orders'
        
        # Execute focused search
        schema = self.get_table_schema()
        results = {}
        
        if search_focus == 'products' and 'products' in schema:
            sql = """
                SELECT name, description, price, stock, category, village, farmer
                FROM products 
                WHERE name LIKE %s OR description LIKE %s OR category LIKE %s
                ORDER BY product_id DESC 
                LIMIT %s
            """
            params = (f'%{query}%', f'%{query}%', f'%{query}%', limit)
            product_results = self.execute_query(sql, params)
            if product_results:
                results['products'] = {
                    'columns': ['name', 'description', 'price', 'stock', 'category'],
                    'data': product_results
                }
        
        elif search_focus == 'users' and 'users' in schema:
            sql = """
                SELECT username, email, phone, address
                FROM users 
                WHERE username LIKE %s OR email LIKE %s OR address LIKE %s
                LIMIT %s
            """
            params = (f'%{query}%', f'%{query}%', f'%{query}%', limit)
            user_results = self.execute_query(sql, params)
            if user_results:
                results['users'] = {
                    'columns': ['username', 'email', 'phone', 'address'],
                    'data': user_results
                }
        
        elif search_focus == 'orders' and 'orders' in schema:
            sql = """
                SELECT o.order_id, u.username, p.name as product_name, o.quantity, o.total_price, o.order_status
                FROM orders o
                LEFT JOIN users u ON o.user_id = u.user_id
                LEFT JOIN products p ON o.product_id = p.product_id
                WHERE p.name LIKE %s OR u.username LIKE %s OR o.order_status LIKE %s
                LIMIT %s
            """
            params = (f'%{query}%', f'%{query}%', f'%{query}%', limit)
            order_results = self.execute_query(sql, params)
            if order_results:
                results['orders'] = {
                    'columns': ['order_id', 'username', 'product_name', 'quantity', 'total_price', 'order_status'],
                    'data': order_results
                }
        
        # If no focused results, do general search
        if not results:
            results = self.search_across_tables(query, limit)
        
        return {
            'query': query,
            'search_focus': search_focus,
            'results': results
        }

class DatabaseTools:
    """Database tools for agent use"""
    
    def __init__(self, config):
        self.config = config
        self.db_manager = None
        
        # 处理字典或对象配置
        if isinstance(config, dict):
            enable_db = config.get('enable_database', False)
            host = config.get('host', 'localhost')
            database = config.get('database', 'llm_agent_db')
            user = config.get('user', 'root')
            password = config.get('password', '')
            port = config.get('port', 3306)
        else:
            # 假设是对象，使用属性
            enable_db = config.enable_database
            host = config.db_host
            database = config.db_name
            user = config.db_user
            password = config.db_password
            port = config.db_port
        
        if enable_db:
            db_config = {
                'host': host,
                'database': database,
                'user': user,
                'password': password,
                'port': port
            }
            self.db_manager = DatabaseManager(db_config)
    
    def search_knowledge_base(self, query: str, category: str = None, limit: int = 5) -> Dict[str, Any]:
        """Search knowledge base for relevant information"""
        if not self.db_manager:
            return {"status": "error", "message": "Database tools not initialized"}
        
        try:
            # Use smart search instead of fixed table query
            results = self.db_manager.smart_search(query, category, limit)
            
            # Log the search results
            total_results = sum(len(table_data['data']) for table_data in results['results'].values())
            logging.info(f"智能搜索: '{query}' -> 找到 {total_results} 条结果 (表: {list(results['results'].keys())})")
            
            return {
                "status": "success",
                "query": query,
                "search_focus": results['search_focus'],
                "total_results": total_results,
                "results": results['results']
            }
            
        except Exception as e:
            logging.error(f"Knowledge base search failed: {e}")
            return {"status": "error", "message": f"Search failed: {str(e)}"}
    
    def get_context_for_query(self, user_id: str, query: str) -> Dict[str, Any]:
        """Get context information for a user query"""
        if not self.db_manager:
            return {}
        
        try:
            context = {}
            
            # Get user profile if user_id provided
            if user_id and user_id != 'default':
                sql = "SELECT username, email, phone, address FROM users WHERE user_id = %s"
                user_profile = self.db_manager.execute_query(sql, (user_id,))
                if user_profile:
                    context['user_profile'] = user_profile[0]
            
            # Search for relevant information
            search_results = self.db_manager.smart_search(query, limit=3)
            if search_results['results']:
                context['relevant_info'] = search_results
            
            return context
            
        except Exception as e:
            logging.error(f"Context search failed: {e}")
            return {}

def create_database_tools(config):
    """Factory function to create database tools instance"""
    return DatabaseTools(config)