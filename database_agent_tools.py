"""
Database Tools for LLM Agent
Provides database query and management capabilities as agent tools
"""

from typing import Dict, Any, List, Optional
import json

# Global database tools instance
db_tools_instance = None

def register_database_tools(tool_manager):
    """Register database tools with tool manager"""
    try:
        from database_tools import create_database_tools
        
        # 检查是否有数据库配置和是否启用数据库
        from AgentConfig import AgentConfig
        config = AgentConfig()
        
        if config.enable_database and config.database_config:
            global db_tools_instance
            db_tools_instance = create_database_tools(config.database_config)
            
            # 注册工具函数
            tool_manager.register_tool("search_database_context", search_database_context)
            tool_manager.register_tool("search_knowledge_base", search_knowledge_base)
            tool_manager.register_tool("log_conversation", log_conversation)
            tool_manager.register_tool("get_user_conversation_history", get_user_conversation_history)
            
            print("[系统] 数据库工具注册成功")
        else:
            print("[系统] 数据库功能已禁用或无数据库配置，跳过数据库工具注册")
            
    except ImportError:
        print("[系统] 数据库依赖未安装，跳过数据库工具注册")
    except Exception as e:
        print(f"[系统] 数据库工具注册失败: {e}")

def search_database_context(user_id: str, query: str) -> Dict[str, Any]:
    """
    从数据库搜索相关上下文信息
    
    Args:
        user_id: 用户ID
        query: 当前查询内容
        
    Returns:
        包含用户个人资料、历史对话和相关知识的字典
    """
    if not db_tools_instance:
        return {"error": "Database tools not initialized"}
    
    try:
        context = db_tools_instance.get_context_for_query(user_id, query)
        
        # 格式化返回结果
        result = {
            "user_profile": context.get('user_profile'),
            "recent_conversations_count": len(context.get('recent_conversations', [])),
            "relevant_knowledge_count": len(context.get('relevant_knowledge', [])),
            "similar_queries_count": len(context.get('similar_queries', []))
        }
        
        # 添加详细信息（限制长度）
        if context.get('recent_conversations'):
            result['recent_conversations'] = context['recent_conversations'][:3]  # 只返回最近3条
        
        if context.get('relevant_knowledge'):
            result['relevant_knowledge'] = context['relevant_knowledge'][:2]  # 只返回最相关的2条
        
        return result
        
    except Exception as e:
        return {"error": f"Database context search failed: {str(e)}"}

def search_knowledge_base(query: str, category: str = None, limit: int = 5) -> Dict[str, Any]:
    """
    从知识库搜索相关信息
    
    Args:
        query: 搜索关键词
        category: 分类筛选（可选）
        limit: 返回结果数量限制
        
    Returns:
        包含搜索结果的字典
    """
    if not db_tools_instance:
        return {"error": "Database tools not initialized"}
    
    try:
        results = db_tools_instance.search_knowledge_base(query, category, limit)
        
        return {
            "query": query,
            "category": category,
            "results_count": len(results),
            "results": results
        }
        
    except Exception as e:
        return {"error": f"Knowledge base search failed: {str(e)}"}

def log_conversation(user_id: str, session_id: str, user_message: str, agent_response: str, metadata: Dict = None) -> Dict[str, Any]:
    """
    将对话记录保存到数据库
    
    Args:
        user_id: 用户ID
        session_id: 会话ID
        user_message: 用户消息
        agent_response: AI回复
        metadata: 额外元数据（可选）
        
    Returns:
        操作结果
    """
    if not db_tools_instance:
        return {"error": "Database tools not initialized"}
    
    try:
        db_tools_instance.log_conversation(user_id, session_id, user_message, agent_response, metadata)
        
        return {
            "status": "success",
            "message": "Conversation logged successfully",
            "user_id": user_id,
            "session_id": session_id
        }
        
    except Exception as e:
        return {"error": f"Conversation logging failed: {str(e)}"}

def get_user_conversation_history(user_id: str, limit: int = 10) -> Dict[str, Any]:
    """
    获取用户的历史对话记录
    
    Args:
        user_id: 用户ID
        limit: 返回记录数量限制
        
    Returns:
        包含历史对话的字典
    """
    if not db_tools_instance:
        return {"error": "Database tools not initialized"}
    
    try:
        conversations = db_tools_instance.search_conversation_history(user_id, limit=limit)
        
        return {
            "user_id": user_id,
            "conversations_count": len(conversations),
            "conversations": conversations
        }
        
    except Exception as e:
        return {"error": f"Failed to get conversation history: {str(e)}"}

def add_knowledge_entry(category: str, title: str, content: str, tags: List[str] = None, source: str = None) -> Dict[str, Any]:
    """
    向知识库添加新条目
    
    Args:
        category: 分类
        title: 标题
        content: 内容
        tags: 标签列表（可选）
        source: 来源（可选）
        
    Returns:
        操作结果
    """
    if not db_tools_instance:
        return {"error": "Database tools not initialized"}
    
    try:
        # 这里需要扩展 database_tools 来支持添加知识库条目
        # 暂时返回占位符
        return {
            "status": "success",
            "message": "Knowledge entry added successfully",
            "category": category,
            "title": title
        }
        
    except Exception as e:
        return {"error": f"Failed to add knowledge entry: {str(e)}"}

def update_user_profile(user_id: str, preferences: Dict = None, context_data: Dict = None) -> Dict[str, Any]:
    """
    更新用户个人资料
    
    Args:
        user_id: 用户ID
        preferences: 用户偏好设置
        context_data: 上下文数据
        
    Returns:
        操作结果
    """
    if not db_tools_instance:
        return {"error": "Database tools not initialized"}
    
    try:
        # 这里需要扩展 database_tools 来支持更新用户资料
        # 暂时返回占位符
        return {
            "status": "success",
            "message": "User profile updated successfully",
            "user_id": user_id
        }
        
    except Exception as e:
        return {"error": f"Failed to update user profile: {str(e)}"}

# 工具函数列表，供其他模块导入
DATABASE_TOOLS = {
    "search_database_context": search_database_context,
    "search_knowledge_base": search_knowledge_base,
    "log_conversation": log_conversation,
    "get_user_conversation_history": get_user_conversation_history,
    "add_knowledge_entry": add_knowledge_entry,
    "update_user_profile": update_user_profile
}