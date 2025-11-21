#!/usr/bin/env python3
"""
LLM Auto Agent Web 界面
基于 Flask 的 Web 交互界面
"""

import os
import sys
import json
import logging
import threading
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB 文件上传限制

# 全局变量存储 Agent 实例和配置
agent_instances = {}

class WebAgentManager:
    """Web 界面专用的 Agent 管理器"""
    
    def __init__(self):
        self.sessions = {}
    
    def get_agent_for_session(self, session_id, user_input=None):
        """获取或创建会话的 Agent 实例"""
        if session_id not in self.sessions:
            try:
                # 动态导入 Agent 模块
                from agent import ReactAgent
                from AgentConfig import AgentConfig
                
                # 创建配置对象
                config = AgentConfig()
                
                # 从会话中加载配置（如果存在）
                if 'agent_config' in session:
                    config_dict = session['agent_config']
                    config.api_key = config_dict.get('api_key', '')
                    config.model_name = config_dict.get('model_name', 'deepseek-chat')
                    config.base_url = config_dict.get('base_url', 'https://api.deepseek.com/v1')
                    config.max_steps = config_dict.get('max_steps', 10)
                    config.enable_database = config_dict.get('enable_database', False)
                    config.show_system_message = config_dict.get('show_system_message', False)
                    config.prompt_refresh_interval = config_dict.get('prompt_refresh_interval', 3)
                    config.conda_env = config_dict.get('conda_env', '')
                
                # 创建新的 Agent 实例
                agent = ReactAgent(config)
                
                self.sessions[session_id] = {
                    'agent': agent,
                    'created_at': datetime.now(),
                    'message_count': 0
                }
                logger.info(f"为会话 {session_id} 创建新的 Agent 实例")
                
            except Exception as e:
                logger.error(f"创建 Agent 实例失败: {e}")
                return None
        
        return self.sessions[session_id]['agent']
    
    def process_message(self, session_id, user_input):
        """处理用户消息并返回结果"""
        try:
            agent = self.get_agent_for_session(session_id)
            if not agent:
                return "无法初始化 AI 助手"
            
            # 直接调用 Agent 的 run 方法，传递用户输入
            result = agent.run(user_input=user_input, timeout=30)
            
            # 更新消息计数
            self.sessions[session_id]['message_count'] += 1
            
            return result
            
        except Exception as e:
            logger.error(f"处理消息时出错: {e}")
            return f"处理消息时出错: {str(e)}"
    
    def cleanup_old_sessions(self):
        """清理旧的会话"""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session_data in self.sessions.items():
            session_age = current_time - session_data['created_at']
            if session_age.total_seconds() > 3600:  # 1小时过期
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
            logger.info(f"清理过期会话: {session_id}")

# 创建管理器实例
agent_manager = WebAgentManager()

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def process_message():
    """处理用户消息"""
    try:
        data = request.get_json()
        user_input = data.get('message', '').strip()
        session_id = data.get('session_id', 'default')
        
        if not user_input:
            return jsonify({
                'success': False,
                'error': '消息内容不能为空'
            })
        
        logger.info(f"处理用户消息 - 会话: {session_id}, 输入: {user_input[:50]}...")
        
        # 直接处理消息
        result = agent_manager.process_message(session_id, user_input)
        
        # 格式化响应
        if isinstance(result, str):
            response_text = result
        elif isinstance(result, dict):
            response_text = result.get('response', str(result))
        else:
            response_text = str(result)
        
        logger.info(f"AI 响应: {response_text[:100]}...")
        
        return jsonify({
            'success': True,
            'response': response_text,
            'session_id': session_id
        })
        
    except Exception as e:
        logger.error(f"处理消息时出错: {e}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        })

@app.route('/api/settings', methods=['POST'])
def update_settings():
    """更新设置"""
    try:
        data = request.get_json()
        
        # 创建配置字典
        config_dict = {
            'api_key': data.get('api_key', ''),
            'model_name': data.get('model_name', 'deepseek-chat'),
            'base_url': data.get('base_url', 'https://api.deepseek.com/v1'),
            'max_steps': data.get('max_steps', 10),
            'enable_database': data.get('enable_database', False),
            'show_system_message': data.get('show_system_message', False),
            'prompt_refresh_interval': data.get('prompt_refresh_interval', 3),
            'conda_env': data.get('conda_env', '')
        }
        
        # 保存配置到会话
        session['agent_config'] = config_dict
        
        # 更新环境变量
        os.environ['DEEPSEEK_API_KEY'] = config_dict['api_key']
        
        return jsonify({
            'success': True,
            'message': '设置已更新'
        })
        
    except Exception as e:
        logger.error(f"更新设置时出错: {e}")
        return jsonify({
            'success': False,
            'error': f'更新设置失败: {str(e)}'
        })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """上传文件到知识库"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': '没有选择文件'
            })
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': '没有选择文件'
            })
        
        # 检查文件类型
        allowed_extensions = {'.txt', '.pdf', '.doc', '.docx', '.md', '.json'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({
                'success': False,
                'error': f'不支持的文件类型: {file_ext}'
            })
        
        # 保存文件
        upload_dir = os.path.join(project_root, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        
        logger.info(f"文件上传成功: {filename}")
        
        return jsonify({
            'success': True,
            'message': f'文件 {file.filename} 上传成功',
            'filename': filename
        })
        
    except Exception as e:
        logger.error(f"文件上传失败: {e}")
        return jsonify({
            'success': False,
            'error': f'文件上传失败: {str(e)}'
        })

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'active_sessions': len(agent_manager.sessions)
    })

if __name__ == '__main__':
    print("🚀 启动 LLM Auto Agent Web 界面...")
    print(f"📁 项目路径: {project_root}")
    print("🌐 访问地址: http://127.0.0.1:5000")
    print("⏹️  按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    # 启动会话清理定时器
    def cleanup_scheduler():
        import time
        while True:
            time.sleep(300)  # 每5分钟清理一次
            agent_manager.cleanup_old_sessions()
    
    cleanup_thread = threading.Thread(target=cleanup_scheduler, daemon=True)
    cleanup_thread.start()
    
    # 启动 Flask 应用
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )