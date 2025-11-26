"""
LLM Agent with React pattern and tool usage
Enhanced version with better database tool integration
"""

import logging
import time
import json
from typing import Dict, List, Any, Optional, Generator
from config_manager import ConfigManager
from Toolmanager import ToolManager
from system_prompts import get_system_prompt

logger = logging.getLogger("LLM_Agent")

# Check if database tools are available
try:
    from database_tools import create_database_tools
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    logger.warning("Database tools not available")

class ReactAgent:
    """ReAct Agent with enhanced database tool integration"""
    
    def __init__(self, config: Optional[ConfigManager] = None):
        # 支持旧的 AgentConfig 和新的 ConfigManager
        if config is None:
            self.config = ConfigManager()
        elif hasattr(config, 'config_data'):
            self.config = config
        else:
            # 如果是旧的 AgentConfig，转换为新的 ConfigManager
            self.config = ConfigManager()
            # 映射旧配置属性到新配置结构
            if hasattr(config, 'api_key'):
                self.config.set('api.deepseek.api_key', config.api_key)
            if hasattr(config, 'model_name'):
                self.config.set('api.deepseek.default_model', config.model_name)
            if hasattr(config, 'base_url'):
                self.config.set('api.deepseek.base_url', config.base_url)
            if hasattr(config, 'max_steps'):
                self.config.set('max_steps', config.max_steps)
            if hasattr(config, 'refresh_prompt_interval'):
                self.config.set('prompt_refresh_interval', config.refresh_prompt_interval)
            if hasattr(config, 'show_system_messages'):
                self.config.set('debug.show_system_messages', config.show_system_messages)
            if hasattr(config, 'conda_env'):
                self.config.set('tools.conda_env', config.conda_env)
            elif hasattr(config, 'conda'):
                self.config.set('tools.conda_env', config.conda)
            if hasattr(config, 'enable_database'):
                self.config.set('database.enabled', config.enable_database)
            if hasattr(config, 'database_config'):
                self.config.set('database', config.database_config)
            if hasattr(config, 'project_directory'):
                self.config.set('project_directory', config.project_directory)
        
        # Initialize components
        self.tool_manager = ToolManager(self.config)
        self.db_tools = None
        self.system_prompt = ""
        self.last_prompt_refresh = 0
        
        # Initialize tools and database
        self._init_tools()
        self._init_database_tools()
        self._refresh_system_prompt()
        
        logger.info("ReActAgent 初始化完成")
    
    def _init_tools(self):
        """Initialize all available tools"""
        try:
            # Register agent tools
            from agent_tools import register_agent_tools
            register_agent_tools(self.tool_manager)
            
            # Register database tools if available
            if DATABASE_AVAILABLE:
                from database_agent_tools import register_database_tools
                db_config = self._get_database_config()
                register_database_tools(self.tool_manager, db_config)
            
            logger.info("工具初始化完成")
        except Exception as e:
            logger.error(f"工具初始化失败: {e}")
    
    def _get_database_config(self):
        """Get database configuration in compatible format"""
        db_config_dict = {
            'enable_database': self.config.get('database.enabled', False),
            'host': self.config.get('database.host', 'localhost'),
            'user': self.config.get('database.user', 'root'),
            'password': self.config.get('database.password', ''),
            'database': self.config.get('database.database', 'llm_agent_db'),
            'port': self.config.get('database.port', 3306)
        }
        return db_config_dict
    
    def _init_database_tools(self):
        """Initialize database tools (if enabled)"""
        if not self.config.get('database.enabled', False):
            logger.info("数据库功能已禁用")
            return
        
        if not DATABASE_AVAILABLE:
            logger.warning("数据库依赖未安装，跳过数据库功能")
            return
        
        try:
            db_config = self._get_database_config()
            if db_config['enable_database']:
                self.db_tools = create_database_tools(db_config)
                logger.info("数据库工具初始化成功")
        except Exception as e:
            logger.error(f"数据库工具初始化失败: {e}")
            self.db_tools = None
    
    def _refresh_system_prompt(self):
        """Refresh system prompt based on configuration"""
        prompt_type = self.config.get('system_prompt.type', 'database_enhanced')
        self.system_prompt = get_system_prompt(prompt_type)
        self.last_prompt_refresh = time.time()
        logger.info(f"系统提示已加载，类型: {prompt_type}")
    
    def _should_refresh_prompt(self):
        """Check if system prompt should be refreshed"""
        interval = self.config.get('prompt_refresh_interval', 3600)  # 1 hour default
        return time.time() - self.last_prompt_refresh > interval
    
    def run(self, user_input: str, timeout: int = 60) -> Dict[str, Any]:
        """Run agent with user input and return result"""
        start_time = time.time()
        
        try:
            # Refresh prompt if needed
            if self._should_refresh_prompt():
                self._refresh_system_prompt()
            
            # Initialize API manager
            from api_manager import APIManager
            api_manager = APIManager(self.config)
            
            # Prepare initial messages
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_input}
            ]
            
            max_steps = self.config.get('max_steps', 10)
            current_step = 0
            
            while current_step < max_steps:
                # Check timeout
                if time.time() - start_time > timeout:
                    return {
                        "status": "timeout",
                        "message": f"任务超时（{timeout}秒）",
                        "elapsed_time": time.time() - start_time
                    }
                
                # Get LLM response
                response = api_manager.chat_completion(
                    messages=messages,
                    model=self.config.get('api.deepseek.default_model', 'deepseek-chat'),
                    temperature=0.1
                )
                
                if not response:
                    return {
                        "status": "error",
                        "message": "API调用失败",
                        "elapsed_time": time.time() - start_time
                    }
                
                # Add assistant response to messages
                messages.append({"role": "assistant", "content": response})
                
                # Check if response contains action
                if self._contains_action(response):
                    # Parse and execute action
                    action_result = self._execute_action(response)
                    
                    # Add action result to messages
                    messages.append({"role": "user", "content": f"Action Result: {action_result}"})
                    
                    # Check if we should continue
                    if self._is_final_result(action_result):
                        return {
                            "status": "success",
                            "answer": response,
                            "actions": current_step + 1,
                            "elapsed_time": time.time() - start_time
                        }
                else:
                    # No action, return final answer
                    return {
                        "status": "success", 
                        "answer": response,
                        "actions": current_step,
                        "elapsed_time": time.time() - start_time
                    }
                
                current_step += 1
            
            return {
                "status": "max_steps_reached",
                "answer": "达到最大步骤限制",
                "actions": current_step,
                "elapsed_time": time.time() - start_time
            }
            
        except Exception as e:
            logger.error(f"Agent执行失败: {e}")
            return {
                "status": "error",
                "message": f"执行失败: {str(e)}",
                "elapsed_time": time.time() - start_time
            }
    
    def run_stream(self, user_input: str, timeout: int = 60) -> Generator[str, None, Dict[str, Any]]:
        """Run agent with streaming output"""
        start_time = time.time()
        stats = {
            'steps': 0,
            'api_calls': 0,
            'elapsed_time': 0
        }
        
        try:
            # Refresh prompt if needed
            if self._should_refresh_prompt():
                self._refresh_system_prompt()
            
            yield f"系统提示已加载，提供商: {self.config.get('api.default_provider', 'deepseek')}, " \
                  f"模型: {self.config.get('api.deepseek.default_model', 'deepseek-chat')}\n"
            
            # Initialize API manager
            from api_manager import APIManager
            api_manager = APIManager(self.config)
            
            # Prepare initial messages
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_input}
            ]
            
            max_steps = self.config.get('max_steps', 10)
            current_step = 0
            
            while current_step < max_steps:
                # Check timeout
                if time.time() - start_time > timeout:
                    yield f"\n[超时] 任务执行超过{timeout}秒\n"
                    stats['elapsed_time'] = time.time() - start_time
                    return {"status": "timeout", "stats": stats}
                
                # Get LLM response
                response = api_manager.chat_completion(
                    messages=messages,
                    model=self.config.get('api.deepseek.default_model', 'deepseek-chat'),
                    temperature=0.1
                )
                stats['api_calls'] += 1
                
                if not response:
                    yield "\n[错误] API调用失败\n"
                    stats['elapsed_time'] = time.time() - start_time
                    return {"status": "error", "stats": stats}
                
                yield f"\n[思考] {response}\n"
                
                # Add assistant response to messages
                messages.append({"role": "assistant", "content": response})
                
                # Check if response contains action
                if self._contains_action(response):
                    yield "\n[执行动作]...\n"
                    
                    # Parse and execute action
                    action_result = self._execute_action(response)
                    stats['steps'] += 1
                    
                    yield f"[动作结果] {action_result}\n"
                    
                    # Add action result to messages
                    messages.append({"role": "user", "content": f"Action Result: {action_result}"})
                    
                    # Check if we should continue
                    if self._is_final_result(action_result):
                        stats['elapsed_time'] = time.time() - start_time
                        yield f"\n[完成] 任务完成，步骤: {stats['steps']}\n"
                        return {"status": "success", "stats": stats}
                else:
                    # No action, return final answer
                    stats['elapsed_time'] = time.time() - start_time
                    yield f"\n[完成] 直接回答，步骤: {stats['steps']}\n"
                    return {"status": "success", "stats": stats}
                
                current_step += 1
            
            stats['elapsed_time'] = time.time() - start_time
            yield f"\n[警告] 达到最大步骤限制 ({max_steps})\n"
            return {"status": "max_steps_reached", "stats": stats}
            
        except Exception as e:
            logger.error(f"Agent流式执行失败: {e}")
            stats['elapsed_time'] = time.time() - start_time
            yield f"\n[错误] 执行失败: {str(e)}\n"
            return {"status": "error", "stats": stats}
    
    def _contains_action(self, response: str) -> bool:
        """Check if response contains action markers"""
        action_indicators = ["动作", "action", "工具", "tool", "搜索", "search", "查询", "check"]
        return any(indicator in response.lower() for indicator in action_indicators)
    
    def _execute_action(self, response: str) -> str:
        """Parse and execute action from response"""
        try:
            # Enhanced action parsing with database tool priority
            response_lower = response.lower()
            
            # Check for product stock queries
            if "库存" in response_lower or "stock" in response_lower or "有货" in response_lower:
                product_name = self._extract_product_name(response)
                if product_name:
                    return self.tool_manager.execute_tool("check_product_stock", {"product_name": product_name})
            
            # Check for order status queries
            if "订单" in response_lower or "order" in response_lower:
                order_id = self._extract_order_id(response)
                if order_id:
                    return self.tool_manager.execute_tool("check_order_status", {"order_id": order_id})
            
            # Check for general database searches
            if "数据库" in response_lower or "database" in response_lower:
                query = self._extract_query(response, ["搜索", "查询", "search", "find"])
                if query:
                    return self.tool_manager.execute_tool("search_database", {"query": query})
            
            # Fallback to tool manager's action parsing
            return self.tool_manager.parse_and_execute(response)
            
        except Exception as e:
            return f"动作执行失败: {str(e)}"
    
    def _extract_product_name(self, response: str) -> str:
        """Extract product name from response"""
        product_names = [
            "青城山腊肉", "安吉白茶", "元阳红米", "苗银手镯", 
            "宏村竹笋", "阳朔金桔", "湘西腊鱼", "婺源皇菊"
        ]
        
        for product in product_names:
            if product in response:
                return product
        
        # If no specific product found, try to extract from context
        if "腊肉" in response:
            return "青城山腊肉"
        elif "白茶" in response:
            return "安吉白茶"
        elif "红米" in response:
            return "元阳红米"
        
        return ""
    
    def _extract_order_id(self, response: str) -> str:
        """Extract order ID from response"""
        import re
        
        # Look for patterns like "订单3", "order 3", "订单 3"
        patterns = [
            r"订单\s*(\d+)",
            r"order\s*(\d+)",
            r"订单号\s*(\d+)",
            r"order\s*#\s*(\d+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # If no pattern found, look for standalone numbers in order context
        if "订单" in response or "order" in response.lower():
            numbers = re.findall(r'\b\d+\b', response)
            if numbers:
                return numbers[0]  # Return first number found
        
        return ""
    
    def _extract_query(self, response: str, keywords: List[str]) -> str:
        """Extract query from response based on keywords"""
        for keyword in keywords:
            if keyword in response:
                # Simple extraction - in practice, use more sophisticated NLP
                parts = response.split(keyword, 1)
                if len(parts) > 1:
                    query = parts[1].strip()
                    # Clean up the query
                    query = query.split('。')[0].split('！')[0].split('？')[0].strip()
                    return query
        return ""
    
    def _is_final_result(self, action_result: str) -> bool:
        """Check if action result indicates final answer"""
        final_indicators = ["完成", "成功", "找到", "final", "success", "found", "库存", "状态"]
        return any(indicator in action_result.lower() for indicator in final_indicators)