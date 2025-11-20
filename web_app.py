#!/usr/bin/env python3
"""
LLM Auto Agent Web Interface
基于 Townrain/LLM_Auto_Agent 的Web交互界面
"""

import os
import sys
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from agent import ReactAgent
    from AgentConfig import AgentConfig
    print("✅ Agent模块导入成功")
except ImportError as e:
    print(f"⚠️  Agent模块导入失败: {e}")
    print("请确保已安装所有依赖: pip install -r requirements.txt")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'llm_auto_agent_web_secret_key_2024'
CORS(app)

# 全局变量
agent_instance = None

class WebAgentManager:
    """Web界面专用的Agent管理器"""
    
    def __init__(self):
        self.agent = None
        self.config = None
    
    def initialize_agent(self, api_key=None, use_database=False, db_config=None):
        """初始化Agent实例"""
        try:
            # 设置环境变量
            if api_key:
                os.environ['DEEPSEEK_API_KEY'] = api_key
            
            # 创建配置
            self.config = AgentConfig()
            
            # 配置数据库（如果启用）
            if use_database and db_config:
                self.config.use_database = True
                self.config.db_host = db_config.get('host', 'localhost')
                self.config.db_port = db_config.get('port', 3306)
                self.config.db_user = db_config.get('user', 'root')
                self.config.db_password = db_config.get('password', '')
                self.config.db_name = db_config.get('database', 'llm_agent')
            else:
                self.config.use_database = False
            
            # 创建Agent实例
            self.agent = ReactAgent(self.config)
            
            logger.info("✅ Agent初始化成功")
            return True, "Agent初始化成功"
            
        except Exception as e:
            logger.error(f"❌ Agent初始化失败: {e}")
            return False, f"Agent初始化失败: {str(e)}"
    
    def process_message(self, user_input, conversation_id=None):
        """处理用户消息"""
        if not self.agent:
            return False, "Agent未初始化，请先配置API Key"
        
        try:
            # 运行Agent
            result = self.agent.run(user_input)
            
            # 格式化响应
            if isinstance(result, dict):
                return True, result
            else:
                return True, {"response": str(result), "type": "text"}
                
        except Exception as e:
            logger.error(f"❌ 消息处理失败: {e}")
            return False, f"处理消息时出错: {str(e)}"

# 创建管理器实例
agent_manager = WebAgentManager()

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/api/initialize', methods=['POST'])
def initialize_agent():
    """初始化Agent"""
    try:
        data = request.get_json()
        
        api_key = data.get('api_key')
        use_database = data.get('use_database', False)
        db_config = data.get('db_config', {})
        
        success, message = agent_manager.initialize_agent(api_key, use_database, db_config)
        
        return jsonify({
            'success': success,
            'message': message
        })
        
    except Exception as e:
        logger.error(f"初始化API错误: {e}")
        return jsonify({
            'success': False,
            'message': f"初始化失败: {str(e)}"
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """处理聊天消息"""
    try:
        data = request.get_json()
        user_input = data.get('message', '')
        conversation_id = data.get('conversation_id')
        
        if not user_input.strip():
            return jsonify({
                'success': False,
                'message': '消息不能为空'
            })
        
        success, result = agent_manager.process_message(user_input, conversation_id)
        
        return jsonify({
            'success': success,
            'result': result if success else None,
            'message': result if not success else '消息处理成功'
        })
        
    except Exception as e:
        logger.error(f"聊天API错误: {e}")
        return jsonify({
            'success': False,
            'message': f"处理消息时出错: {str(e)}"
        }), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """上传知识库文件"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': '没有选择文件'
            })
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': '没有选择文件'
            })
        
        # 检查文件类型
        allowed_extensions = {'txt', 'pdf', 'doc', 'docx', 'md', 'json'}
        file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        
        if file_extension not in allowed_extensions:
            return jsonify({
                'success': False,
                'message': f'不支持的文件类型: {file_extension}'
            })
        
        # 保存文件
        upload_dir = os.path.join(current_dir, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        logger.info(f"文件上传成功: {filename}")
        
        return jsonify({
            'success': True,
            'message': f'文件上传成功: {file.filename}',
            'file_path': file_path
        })
        
    except Exception as e:
        logger.error(f"文件上传错误: {e}")
        return jsonify({
            'success': False,
            'message': f"文件上传失败: {str(e)}"
        }), 500

@app.route('/api/confirm_command', methods=['POST'])
def confirm_command():
    """确认系统命令执行"""
    try:
        data = request.get_json()
        command = data.get('command', '')
        confirmed = data.get('confirmed', False)
        
        if not confirmed:
            return jsonify({
                'success': False,
                'message': '用户取消了命令执行'
            })
        
        # 这里可以添加命令执行逻辑
        # 注意：出于安全考虑，实际执行需要谨慎处理
        
        return jsonify({
            'success': True,
            'message': f'命令已确认执行: {command}'
        })
        
    except Exception as e:
        logger.error(f"命令确认错误: {e}")
        return jsonify({
            'success': False,
            'message': f"命令确认失败: {str(e)}"
        }), 500

@app.route('/api/health')
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'agent_initialized': agent_manager.agent is not None
    })

if __name__ == '__main__':
    print("🚀 启动 LLM Auto Agent Web 界面...")
    print("📁 项目路径:", current_dir)
    print("🌐 访问地址: http://127.0.0.1:5000")
    print("⏹️  按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    # 创建必要的目录
    os.makedirs(os.path.join(current_dir, 'uploads'), exist_ok=True)
    os.makedirs(os.path.join(current_dir, 'templates'), exist_ok=True)
    os.makedirs(os.path.join(current_dir, 'static/css'), exist_ok=True)
    os.makedirs(os.path.join(current_dir, 'static/js'), exist_ok=True)
    
    # 启动Flask应用
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )