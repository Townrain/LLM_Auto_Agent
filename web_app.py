#!/usr/bin/env python3
"""
LLM Auto Agent Web Interface
基于Flask的Web交互界面
"""

import os
import json
import threading
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import sys
import importlib.util

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
app.secret_key = 'llm_auto_agent_web_secret_key_2025'
CORS(app)

# 全局变量存储Agent实例和配置
agent_instance = None
agent_config = {}

def load_agent_modules():
    """动态加载Agent模块"""
    try:
        # 尝试导入Agent模块
        from agent import ReactAgent
        from AgentConfig import AgentConfig
        return ReactAgent, AgentConfig
    except ImportError as e:
        print(f"导入Agent模块失败: {e}")
        return None, None

def initialize_agent(api_key=None, use_database=False, db_config=None):
    """初始化Agent实例"""
    global agent_instance, agent_config
    
    ReactAgent, AgentConfig = load_agent_modules()
    if not ReactAgent or not AgentConfig:
        return False, "无法加载Agent模块"
    
    try:
        # 创建配置
        config = AgentConfig()
        
        # 设置API Key
        if api_key:
            config.api_key = api_key
        
        # 设置数据库配置
        if use_database and db_config:
            config.use_database = True
            config.db_host = db_config.get('host', 'localhost')
            config.db_port = db_config.get('port', 3306)
            config.db_user = db_config.get('user', 'root')
            config.db_password = db_config.get('password', '')
            config.db_name = db_config.get('database', 'llm_agent')
        else:
            config.use_database = False
        
        # 创建Agent实例
        agent_instance = ReactAgent(config)
        agent_config = {
            'api_key': api_key,
            'use_database': use_database,
            'db_config': db_config
        }
        
        return True, "Agent初始化成功"
    except Exception as e:
        return False, f"Agent初始化失败: {str(e)}"

def run_agent_in_thread(user_input, callback):
    """在新线程中运行Agent以避免阻塞"""
    def run():
        try:
            if not agent_instance:
                callback({
                    'success': False,
                    'error': 'Agent未初始化，请先配置API Key'
                })
                return
            
            result = agent_instance.run(user_input)
            callback({
                'success': True,
                'response': result
            })
        except Exception as e:
            callback({
                'success': False,
                'error': str(e)
            })
    
    thread = threading.Thread(target=run)
    thread.daemon = True
    thread.start()

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/api/initialize', methods=['POST'])
def api_initialize():
    """初始化Agent"""
    try:
        data = request.json
        api_key = data.get('api_key')
        use_database = data.get('use_database', False)
        db_config = data.get('db_config', {})
        
        success, message = initialize_agent(api_key, use_database, db_config)
        
        return jsonify({
            'success': success,
            'message': message
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """处理聊天请求"""
    try:
        data = request.json
        user_input = data.get('message', '')
        
        if not user_input:
            return jsonify({
                'success': False,
                'error': '消息不能为空'
            })
        
        # 创建回调函数
        def callback(result):
            global chat_result
            chat_result = result
        
        # 在新线程中运行Agent
        run_agent_in_thread(user_input, callback)
        
        return jsonify({
            'success': True,
            'message': '请求已接收，正在处理...'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/check_status', methods=['GET'])
def api_check_status():
    """检查Agent状态"""
    global agent_instance
    
    return jsonify({
        'initialized': agent_instance is not None,
        'config': agent_config
    })

@app.route('/api/confirm_command', methods=['POST'])
def api_confirm_command():
    """确认系统命令执行"""
    try:
        data = request.json
        command = data.get('command', '')
        confirmed = data.get('confirmed', False)
        
        if not confirmed:
            return jsonify({
                'success': False,
                'error': '用户取消了命令执行'
            })
        
        # 这里可以添加命令执行逻辑
        # 注意：出于安全考虑，实际执行需要谨慎处理
        
        return jsonify({
            'success': True,
            'message': f'命令已确认: {command}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/upload_knowledge', methods=['POST'])
def api_upload_knowledge():
    """上传知识库文件"""
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
        allowed_extensions = {'txt', 'pdf', 'doc', 'docx', 'md', 'json'}
        if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            return jsonify({
                'success': False,
                'error': '不支持的文件类型'
            })
        
        # 保存文件
        upload_dir = 'knowledge_base'
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.filename)
        file.save(file_path)
        
        return jsonify({
            'success': True,
            'message': f'文件 {file.filename} 上传成功',
            'file_path': file_path
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    print("启动LLM Auto Agent Web界面...")
    print("访问地址: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)