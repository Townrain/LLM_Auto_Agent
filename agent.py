

import json
import os
import platform
import requests
import time

from string import Template
from typing import List, Dict, Any, Optional
from prompt_template import react_system_prompt_template
import agent_tools
from Toolmanager import ToolManager
from AgentConfig import AgentConfig
from ConversationManager import ConversationManager


def is_web_environment() -> bool:
    """检测是否在Web环境中运行""" 
    return 'FLASK_RUN_FROM_CLI' in os.environ or 'WERKZEUG_RUN_MAIN' in os.environ

class ReactAgent:
    """ReAct Agent主类，整合所有功能""" 
    
    def __init__(self, config: Optional[AgentConfig] = None):
        self.config = config or AgentConfig()
        self.conversation = ConversationManager(self.config)
        self.tool_manager = ToolManager()
        
        # 初始化数据库工具（可选）
        self.db_tools = None
        if self.config.enable_database and self.config.database_config:
            try:
                # 尝试导入数据库工具
                from database_tools import create_database_tools
                self.db_tools = create_database_tools(self.config.database_config)
                print("[系统] 数据库工具初始化成功")
            except ImportError:
                print("[系统] 数据库依赖未安装，跳过数据库功能")
            except Exception as e:
                print(f"[系统] 数据库工具初始化失败: {e}")
        else:
            print("[系统] 数据库功能已禁用")
        
    def get_operating_system_name(self) -> str:
        """获取操作系统名称""" 
        os_map = {
            "Darwin": "macOS",
            "Windows": "Windows", 
            "Linux": "Linux"
        }
        return os_map.get(platform.system(), "Unknown")
        
    def render_system_prompt(self) -> str:
        """渲染系统提示模板""" 
        tool_list = self.tool_manager.get_tool_list()
        
        # 如果数据库工具可用，添加到工具列表
        if self.db_tools:
            tool_list += """ 
- search_database_context: 从数据库搜索相关上下文信息，包括用户历史对话、个人资料和知识库
- log_conversation: 将对话记录保存到数据库
- search_knowledge_base: 从知识库搜索相关信息
""" 
        
        return Template(react_system_prompt_template).substitute(
            operating_system=self.get_operating_system_name(),
            tool_list=tool_list,
        )

    def collect_database_context(self, user_id: str, user_input: str) -> Dict[str, Any]:
        """从数据库收集相关上下文信息""" 
        if not self.db_tools:
            return {}
        
        try:
            context = self.db_tools.get_context_for_query(user_id, user_input)
            
            # 构建上下文摘要
            context_summary = []
            
            if context['user_profile']:
                context_summary.append("用户个人资料可用")
            
            if context['recent_conversations']:
                context_summary.append(f"找到 {len(context['recent_conversations'])} 条历史对话")
            
            if context['relevant_knowledge']:
                context_summary.append(f"找到 {len(context['relevant_knowledge'])} 条相关知识")
            
            if context['similar_queries']:
                context_summary.append(f"找到 {len(context['similar_queries'])} 条相似查询")
            
            if context_summary:
                print(f"[系统] 数据库上下文: {', '.join(context_summary)}")
            
            return context
            
        except Exception as e:
            print(f"[系统] 数据库上下文收集失败: {e}")
            return {}

    def parse_ai_response(self, content: str) -> Dict[str, Any]:
        """解析AI响应内容，将字符串形式返回转化为json""" 
        try:
            if self.config.show_system_messages:
                print(f"[系统] 解析AI响应内容: {content}")
            return json.loads(content)
        except json.JSONDecodeError:
            if self.config.show_system_messages:
                print("无法解析 JSON 响应，可能是格式错误")
            raise
            
    def handle_final_answer(self, response_json: Dict[str, Any]) -> str:
        """处理最终答案""" 
        final_answer = response_json['final_answer']
        
        # 在Web环境中不打印到控制台，直接返回结果
        if not is_web_environment():
            print(f"Answer: {final_answer}")
                
        interaction_count = self.conversation.increment_interaction()
        if self.config.show_system_messages:
            print(f"[系统] 完成第 {interaction_count} 轮交互（final_answer）")
            
        return final_answer
        
    def handle_action(self, response_json: Dict[str, Any]) -> None:
        """处理AI动作执行""" 
        action_str = response_json["action"]
        if self.config.show_system_messages:
            print(f"[系统] 执行动作: {action_str}")
            
        try:
            if self.config.show_system_messages:
                print(f"[系统] 正在解析函数调用: {action_str}")
            func_name = self.tool_manager.parse_action_list(action_str)
            result = self.tool_manager.execute_action_list(func_name)
            self.conversation.add_observation(str(result))
            
            if self.config.show_system_messages:
                print(f"观察结果: {result}")
                print(f"[系统] 当前发送总请求数量: {len(self.conversation.messages)}")
                
        except ValueError as e:
            self.conversation.add_error_observation(str(e))
            if self.config.show_system_messages:
                print(f"工具调用错误: {e}")
                print("[系统] 已将错误信息返回给AI")
                
        except Exception as e:
            error_msg = f"工具执行失败: {str(e)}"
            self.conversation.add_error_observation(error_msg)
            if self.config.show_system_messages:
                print(f"工具执行出错: {e}")
                print("[系统] 已将错误信息返回给AI")
                
    def get_user_input(self, prompt: str = "Question: ") -> str:
        """获取用户输入""" 
        # 在Web环境中，返回默认值而不是等待输入
        if is_web_environment():
            return "继续处理"
        return input(prompt)
        
    def call_deepseek_api(self, messages: List[Dict[str, str]]) -> str:
        """调用 DeepSeek API""" 
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config.model_name,
            "messages": messages,
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.config.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                raise Exception(f"API调用失败: {response.status_code} - {response.text}")
                
        except Exception as e:
            raise Exception(f"DeepSeek API调用错误: {str(e)}")
        
    def process_turn(self) -> str:
        """处理一轮对话，返回结果或None表示继续""" 
        try:
            # 调用 DeepSeek API
            content = self.call_deepseek_api(self.conversation.messages)
            self.conversation.add_message("assistant", content)
            
            if self.config.show_system_messages:
                print("[系统]模型完整回复:", content)
                
            # 解析AI响应
            try:
                response_json = self.parse_ai_response(content)
            except :
                obs_msg = '{"Incorrect_answer_format": "回答解析失败，请检查回复是否为合理json格式后重新回答"}'
                self.conversation.add_message("user", obs_msg)
                return None

            if "final_answer" in response_json:
                final_result = self.handle_final_answer(response_json)
                return final_result  # 返回最终答案
                
            elif "action" in response_json:
                self.handle_action(response_json)
                return None  # 继续AI推理
                
            else:
                if self.config.show_system_messages:
                    print("[系统] AI响应中没有找到 'final_answer' 或 'action' 字段")
                    print(f"[系统] 响应内容: {response_json}")
                return None
                
        except json.JSONDecodeError:
            return None
        except Exception as e:
            if self.config.show_system_messages:
                print(f"API 调用失败: {e}")
            return f"API调用失败: {str(e)}"  # 出错时返回错误信息

    def _create_enhanced_input(self, user_input: str, user_id: str) -> str:
        """ 
        通过数据库上下文增强用户输入
        
        Args:
            user_input: 原始用户输入
            user_id: 用户ID
            
        Returns:
            str: 增强后的用户输入字符串
        """ 
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
            
    def run(self, user_input: str = None, user_id: str = "default_user", timeout: int = 30) -> str:
        """ 
        运行Agent主循环
        
        Args:
            user_input (str, optional): 用户输入. Defaults to None.
            user_id (str, optional): 用户ID. Defaults to "default_user".
            timeout (int, optional): 最大执行时间（秒）. Defaults to 30.
            
        Returns:
            str: 最终答案
        """ 
        if not is_web_environment():
            print("=== ReAct Agent 启动 ===")
        
        start_time = time.time()
        
        # 初始用户输入
        if user_input is None:
            user_input = self.get_user_input()
        
        system_prompt = self.render_system_prompt()
        enhanced_input = self._create_enhanced_input(user_input, user_id)
        self.conversation.add_system_message(enhanced_input, system_prompt)
        
        step_count = 0
        while step_count < self.config.max_steps:
            if time.time() - start_time > timeout:
                return "请求超时，请重试或简化您的问题"
            
            step_count += 1
            
            result = self.process_turn()
            
            if result is not None:
                return result
            
            if self.conversation.should_refresh_prompt():
                if self.config.show_system_messages:
                    print(f"[系统] 达到 {self.config.refresh_prompt_interval} 轮交互，重新添加系统提示")
                    
                if user_input is None:
                    user_input = self.get_user_input()
                
                system_prompt = self.render_system_prompt()
                enhanced_input = self._create_enhanced_input(user_input, user_id)
                self.conversation.refresh_context_with_prompt(enhanced_input, system_prompt)
                
                if self.config.show_system_messages:
                    print(f"[系统] 系统提示已刷新，当前 {len(self.conversation.messages)} 条上下文消息")
            
            step_count = 0
                
        if not is_web_environment():
            print("任务未完成，已达到最大步骤")
        return "任务未完成，已达到最大步骤"

