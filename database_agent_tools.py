"""
Database Agent Tools for LLM Agent
Registers database tools for agent use with improved descriptions and functionality
"""

import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class DatabaseSearchArgs(BaseModel):
    """Arguments for database search"""
    query: str = Field(description="Search query for database")
    category: Optional[str] = Field(default=None, description="Optional category filter")
    limit: int = Field(default=5, description="Maximum number of results to return")

class DatabaseQueryArgs(BaseModel):
    """Arguments for direct database queries"""
    sql_query: str = Field(description="SQL query to execute")

class ProductStockArgs(BaseModel):
    """Arguments for product stock query"""
    product_name: str = Field(description="Name of the product to check stock for")

class OrderStatusArgs(BaseModel):
    """Arguments for order status query"""
    order_id: str = Field(description="Order ID to check status for")

def register_database_tools(tool_manager, config=None):
    """
    Register database tools with the tool manager
    
    Args:
        tool_manager: Tool manager instance
        config: Database configuration (dict or object)
    """
    try:
        from database_tools import create_database_tools
        
        # Handle both dict and object config
        if isinstance(config, dict):
            db_config = config
        else:
            # If config is an object, convert to dict
            db_config = {}
            if hasattr(config, 'enable_database') and config.enable_database:
                db_config = {
                    'enable_database': True,
                    'host': getattr(config, 'db_host', 'localhost'),
                    'user': getattr(config, 'db_user', 'root'),
                    'password': getattr(config, 'db_password', ''),
                    'database': getattr(config, 'db_name', 'llm_agent_db'),
                    'port': getattr(config, 'db_port', 3306)
                }
        
        # Create database tools instance
        db_tools = create_database_tools(db_config)
        
        if db_tools and db_tools.db_manager:
            # Register enhanced database search tool
            tool_manager.register_tool(
                name="search_database",
                description="搜索数据库中的产品信息、库存状态、订单详情、用户数据等。适用于查询具体数据如产品库存、订单状态、用户信息等。对于产品库存查询、订单状态检查等场景优先使用此工具。",
                function=db_tools.search_knowledge_base,
                args_schema=DatabaseSearchArgs
            )
            
            # Register direct SQL query tool
            tool_manager.register_tool(
                name="execute_sql_query",
                description="直接执行SQL查询语句来获取数据库中的精确数据。适用于需要特定数据查询的场景。",
                function=db_tools.execute_sql_query,
                args_schema=DatabaseQueryArgs
            )
            
            # Register product stock check tool
            tool_manager.register_tool(
                name="check_product_stock",
                description="直接查询特定产品的库存状态。输入产品名称，返回库存数量。",
                function=db_tools.check_product_stock,
                args_schema=ProductStockArgs
            )
            
            # Register order status check tool
            tool_manager.register_tool(
                name="check_order_status", 
                description="直接查询特定订单的状态信息。输入订单ID，返回订单状态详情。",
                function=db_tools.check_order_status,
                args_schema=OrderStatusArgs
            )
            
            logger.info("数据库工具注册成功 - 包括搜索、SQL执行、产品库存和订单状态工具")
            return True
        else:
            logger.warning("数据库工具未启用或初始化失败")
            return False
            
    except Exception as e:
        logger.error(f"数据库工具注册失败: {e}")
        return False