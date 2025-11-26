# ReAct Agent - 增强版智能代理
# 集成新的配置管理、日志系统、多LLM支持
# 保持向后兼容性
import json
import logging
import os
import platform
import time
from string import Template
from typing import List, Dict, Any, Optional

# 新的增强模块
from config_manager import ConfigManager, AgentConfig
from logger import logger, log_performance, error_counter
from api_manager import APIManager

# 原有模块（保持兼容性）
from prompt_template import react_system_prompt_template
from Toolmanager import ToolManager
from ConversationManager import ConversationManager

# 数据库工具（可选）
try:
    from database_tools import create_database_tools
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False


def is_web_environment() -> bool:
    """检测是否在Web环境中运行"""
    return 'FLASK_RUN_FROM_CLI' in os.environ or 'WERKZEUG_RUN_MAIN' in os.environ


class ReactAgent:
    """增强版ReAct Agent，集成新功能同时保持向后兼容"""
    
    def __init__(self, config: Optional[ConfigManager] = None):
        # 支持旧的 AgentConfig 和新的 ConfigManager
        if config is None:
            self.config = ConfigManager()
        elif hasattr(config, 'config_data'):
            self.config = config
        else:
            # 如果是旧的 AgentConfig，转换为新的 ConfigManager
            self.config = ConfigManager()
            self.config.set('api.deepseek.api_key', getattr(config, 'API_KEY', ''))
            self.config.set('api.deepseek.default_model', getattr(config, 'MODEL', 'deepseek-chat'))
        
        # 初始化组件
        self.conversation = ConversationManager(self.config)
        self.tool_manager = ToolManager()
        self.api_manager = APIManager(self.config)
        
        # 统计信息
        self.start_time = 0
        self.step_count = 0
        self.task_completed = False
        self.task_result = None
        
        # 初始化数据库工具（可选）
        self.db_tools = None
        self._init_database_tools()
        
        logger.info("ReActAgent 初始化完成")
    
    def _init_database_tools(self):
        """初始化数据库工具（如果启用）"""
        if not self.config.get('database.enabled', False):
            logger.info("数据库功能已禁用")
            return
        
        if not DATABASE_AVAILABLE:
            logger.warning("数据库依赖未安装，跳过数据库功能")
            return
        
        try:
            db_config = self.config.get('database', {})
            if db_config:
                self.db_tools = create_database_tools({
                    'host': db_config.get('host', 'localhost'),
                    'user': db_config.get('user', 'root'),
                    'password': db_config.get('password', ''),
                    'database': db_config.get('database', 'llm_agent_db')
                })
                logger.info("数据库工具初始化成功")
        except Exception as e:
            logger.error(f"数据库工具初始化失败: {e}")
            self.db_tools = None
    
    def get_operating_system_name(self) -> str:
        """获取操作系统名称"""
        os_map = {
            "Darwin": "macOS",
            "Windows": "Windows",
            "Linux": "Linux"
        }
        return os_map.get(platform.system(), "Unknown")
    
    @log_performance
    def render_system_prompt(self) -> str:
        """渲染系统提示模板"""
        tool_list = self.tool_manager.get_tool_list()
        
        # 如果数据库工具可用，添加到工具列表
        if self.db_tools:
            tool_list += """
- search_database_context: 从数据库搜索相关上下文信息，包括用户历史对话、个人资料和知识库
- log_conversation: 将对话记录保存到数据库
- search_knowledge_base: 从知识库搜索相关信息"""
        
        return Template(react_system_prompt_template).substitute(
            operating_system=self.get_operating_system_name(),
            tool_list=tool_list,
        )
    
    @log_performance
    def collect_database_context(self, user_id: str, user_input: str) -> Dict[str, Any]:
        """从数据库收集相关上下文信息"""
        if not self.db_tools:
            return {}
        
        try:
            context = self.db_tools.get_context_for_query(user_id, user_input)
            
            # 构建上下文摘要
            context_summary = []
            
            if context.get('user_profile'):
                context_summary.append("用户个人资料可用")
            
            if context.get('recent_conversations'):
                context_summary.append(f"找到 {len(context['recent_conversations'])} 条历史对话")
            
            if context.get('relevant_knowledge'):
                context_summary.append(f"找到 {len(context['relevant_knowledge'])} 条相关知识")
            
            if context.get('similar_queries'):
                context_summary.append(f"找到 {len(context['similar_queries'])} 条相似查询")
            
            if context_summary:
                logger.info(f"数据库上下文: {', '.join(context_summary)}")
            
            return context
            
        except Exception as e:
            logger.error(f"数据库上下文收集失败: {e}")
            return {}
    
    @log_performance
    def parse_ai_response(self, content: str) -> Dict[str, Any]:
        """解析AI响应内容"""
        try:
            logger.debug(f"解析AI响应: {content[:200]}...")
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON解析失败: {str(e)}")
            logger.debug(f"原始内容: {content}")
            raise
    
    @log_performance
    def handle_final_answer(self, response_json: Dict[str, Any]) -> str:
        """处理最终答案"""
        final_answer = response_json.get('final_answer', '')
        self.task_completed = True
        self.task_result = final_answer
        
        logger.info(f"任务完成，最终答案: {final_answer[:100]}...")
        
        if not is_web_environment():
            print(f"Answer: {final_answer}")
        
        interaction_count = self.conversation.increment_interaction()
        logger.debug(f"完成第 {interaction_count} 轮交互（final_answer）")
        
        return final_answer
    
    @log_performance
    def handle_action(self, response_json: Dict[str, Any]) -> bool:
        """处理AI动作执行"""
        action_str = response_json.get("action", "")
        logger.info(f"执行动作: {action_str[:50]}...")
        
        try:
            logger.debug(f"解析函数调用: {action_str}")
            func_name = self.tool_manager.parse_action_list(action_str)
            result = self.tool_manager.execute_action_list(func_name)
            self.conversation.add_observation(str(result))
            
            logger.debug(f"动作执行结果: {str(result)[:100]}...")
            logger.debug(f"当前发送总请求数量: {len(self.conversation.messages)}")
            return True
            
        except ValueError as e:
            error_msg = f"工具调用错误: {str(e)}"
            self.conversation.add_error_observation(error_msg)
            logger.warning(error_msg)
            
            # 记录错误
            error_count = error_counter.count("tool_error")
            if error_count >= 3:
                logger.error("工具错误次数过多，停止执行")
                return False
            return True
            
        except Exception as e:
            error_msg = f"工具执行失败: {str(e)}"
            self.conversation.add_error_observation(error_msg)
            logger.error(error_msg, exc_info=True)
            
            # 记录错误
            error_count = error_counter.count("tool_error")
            if error_count >= 3:
                logger.error("工具执行错误次数过多，停止执行")
                return False
            return True
    
    def get_user_input(self, prompt: str = "Question: ") -> str:
        """获取用户输入"""
        if is_web_environment():
            return "继续处理"
        try:
            return input(prompt)
        except (KeyboardInterrupt, EOFError):
            logger.info("用户中断输入")
            raise
    
    @log_performance
    def process_turn(self) -> Optional[str]:
        """处理一轮对话，返回结果或None表示继续"""
        try:
            # 调用API
            content = self.api_manager.call_api(self.conversation.messages)
            self.conversation.add_message("assistant", content)
            
            logger.debug(f"API响应: {content[:200]}...")
            
            # 解析AI响应
            try:
                response_json = self.parse_ai_response(content)
            except json.JSONDecodeError:
                obs_msg = '{"Incorrect_answer_format": "回答解析失败，请检查回复是否为合理json格式后重新回答"}'
                self.conversation.add_message("user", obs_msg)
                logger.warning("回答解析失败，已要求AI重新回答")
                return None
            
            # 处理响应
            if "final_answer" in response_json:
                return self.handle_final_answer(response_json)
            elif "action" in response_json:
                success = self.handle_action(response_json)
                if not success:
                    logger.error("动作执行失败，停止任务")
                    return f"任务执行失败: 工具调用错误次数过多"
                return None
            else:
                logger.warning("AI响应中没有找到 'final_answer' 或 'action' 字段")
                logger.debug(f"响应内容: {response_json}")
                return None
                
        except Exception as e:
            logger.error(f"处理轮次失败: {str(e)}", exc_info=True)
            error_count = error_counter.count("api_error")
            if error_count >= 3:
                return f"任务执行失败: {str(e)}"
            return None
    
    @log_performance
    def _create_enhanced_input(self, user_input: str, user_id: str) -> str:
        """通过数据库上下文增强用户输入"""
        db_context = self.collect_database_context(user_id, user_input)
        if not db_context:
            return user_input
        
        context_info = "数据库上下文信息:\n"
        if db_context.get('user_profile'):
            context_info += f"用户个人资料: {db_context['user_profile']}\n"
        if db_context.get('recent_conversations'):
            context_info += f"最近对话: {len(db_context['recent_conversations'])} 条\n"
        if db_context.get('relevant_knowledge'):
            context_info += f"相关知识: {len(db_context['relevant_knowledge'])} 条\n"
        
        return f"{user_input}\n\n[数据库上下文]\n{context_info}"
    
    @log_performance
    def run(self, user_input: str = None, user_id: str = "default_user", timeout: int = None) -> str:
        """
        运行Agent主循环
        
        Args:
            user_input: 用户输入，如果为None则交互式输入
            user_id: 用户ID
            timeout: 超时时间（秒），如果为None则使用配置的值
        """
        timeout = timeout or self.config.get('timeout', 60)
        
        # 重置状态
        self.start_time = time.time()
        self.step_count = 0
        self.task_completed = False
        self.task_result = None
        error_counter.reset()
        
        # 初始用户输入
        if user_input is None and not is_web_environment():
            print("=== ReAct Agent 启动 ===")
            user_input = self.get_user_input()
        elif user_input is None:
            return "错误: Web环境必须提供user_input"
        
        logger.info(f"开始处理任务: {user_input[:50]}...")
        
        # 初始化对话
        system_prompt = self.render_system_prompt()
        enhanced_input = self._create_enhanced_input(user_input, user_id)
        self.conversation.add_system_message(enhanced_input, system_prompt)
        
        logger.debug(f"系统提示已加载，当前提供商: {self.config.get('api.default_provider', 'deepseek')}, "
                    f"模型: {self.config.default_model}")
        
        # 主循环
        max_steps = self.config.get('max_steps', 20)
        while self.step_count < max_steps:
            # 检查超时
            elapsed = time.time() - self.start_time
            if elapsed > timeout:
                logger.warning(f"任务超时（{elapsed:.1f}s > {timeout}s）")
                return f"请求超时（{elapsed:.1f}秒），请重试或简化您的问题"
            
            self.step_count += 1
            logger.debug(f"执行步骤 {self.step_count}/{max_steps}")
            
            # 处理一轮对话
            result = self.process_turn()
            
            if result is not None:
                # 任务完成或出错
                self.task_result = result
                break
            
            # 检查是否需要刷新提示
            if self.conversation.should_refresh_prompt():
                logger.info("刷新系统提示")
                
                system_prompt = self.render_system_prompt()
                enhanced_input = self._create_enhanced_input(user_input, user_id)
                self.conversation.refresh_context_with_prompt(enhanced_input, system_prompt)
                
                logger.debug(f"系统提示已刷新，当前 {len(self.conversation.messages)} 条上下文消息")
        
        # 输出最终结果
        if not self.task_completed:
            logger.warning("任务未完成，已达到最大步骤")
            return "任务未完成，已达到最大步骤"
        
        # 输出统计信息
        stats = self.get_stats()
        logger.info(f"任务完成 - 用时: {stats['elapsed_time']:.1f}s, "
                   f"步骤: {stats['steps']}, API调用: {stats['api_calls']}")
        
        return self.task_result
    
    @log_performance
    def run_stream(self, user_input: str, user_id: str = "default_user", timeout: int = None):
        """流式运行模式"""
        timeout = timeout or self.config.get('timeout', 60)
        
        # 重置状态
        self.start_time = time.time()
        self.step_count = 0
        self.task_completed = False
        self.task_result = None
        error_counter.reset()
        
        logger.info(f"开始流式处理任务: {user_input[:50]}...")
        
        # 初始化对话
        system_prompt = self.render_system_prompt()
        enhanced_input = self._create_enhanced_input(user_input, user_id)
        self.conversation.add_system_message(enhanced_input, system_prompt)
        
        yield f"系统提示已加载，提供商: {self.config.get('api.default_provider', 'deepseek')}, " \
              f"模型: {self.config.default_model}\n"
        
        max_steps = self.config.get('max_steps', 20)
        while self.step_count < max_steps:
            # 检查超时
            elapsed = time.time() - self.start_time
            if elapsed > timeout:
                yield f"\n[错误] 请求超时（{elapsed:.1f}s > {timeout}s）\n"
                logger.warning("任务超时")
                break
            
            self.step_count += 1
            yield f"\n[步骤 {self.step_count}/{max_steps}]...\n"
            
            result = self.process_turn()
            
            if result is not None:
                yield f"\n[完成] {result}\n"
                self.task_completed = True
                break
            
            # 检查是否需要刷新提示
            if self.conversation.should_refresh_prompt():
                yield "\n[系统] 刷新系统提示...\n"
                
                system_prompt = self.render_system_prompt()
                enhanced_input = self._create_enhanced_input(user_input, user_id)
                self.conversation.refresh_context_with_prompt(enhanced_input, system_prompt)
        
        if not self.task_completed:
            yield "\n[警告] 任务未完成，已达到最大步骤\n"
            logger.warning("任务未完成，达到最大步骤")
        
        # 输出统计信息
        stats = self.get_stats()
        yield f"\n[统计] 用时: {stats['elapsed_time']:.1f}s, " \
              f"步骤: {stats['steps']}, API调用: {stats['api_calls']}\n"
    
    def get_stats(self) -> Dict[str, Any]:
        """获取运行统计"""
        api_stats = self.api_manager.get_stats()
        error_stats = error_counter.get_stats()
        
        return {
            "elapsed_time": time.time() - self.start_time if self.start_time else 0,
            "steps": self.step_count,
            "task_completed": self.task_completed,
            "api_calls": api_stats["request_count"],
            "total_tokens": api_stats["total_tokens"],
            "total_cost": api_stats["total_cost"],
            "success_rate": api_stats["success_rate"],
            "errors": error_stats["total_errors"],
            "api_stats": api_stats
        }


# 向后兼容的函数和类
def create_react_agent(config=None):
    """创建ReAct Agent实例（向后兼容）"""
    return ReactAgent(config)


# 保持旧的类名（如果其他地方有引用）
class ReActAgent_V1(ReactAgent):
    """旧的类名，保持向后兼容"""
    pass


if __name__ == "__main__":
    # 测试Agent
    print("测试 ReAct Agent...")
    
    # 创建配置（可以使用旧的AgentConfig或新的ConfigManager）
    # config = AgentConfig()  # 旧的配置方式
    config = ConfigManager()  # 新的配置方式
    
    agent = ReactAgent(config)
    
    # 测试简单对话
    try:
        result = agent.run("计算 15 * 23 等于多少？")
        print(f"\n最终结果: {result}")
        
        # 打印统计
        stats = agent.get_stats()
        print(f"\n运行统计:")
        print(f"  用时: {stats['elapsed_time']:.1f}秒")
        print(f"  步骤: {stats['steps']}")
        print(f"  API调用: {stats['api_calls']}")
        print(f"  Token总数: {stats['total_tokens']}")
        print(f"  预估成本: ${stats['total_cost']:.6f}")
        
    except KeyboardInterrupt:
        print("\n用户中断")
    except Exception as e:
        print(f"\n执行出错: {e}")
        logger.error("测试执行出错", exc_info=True)