"""
LLM Auto Agent Web Interface
基于Flask的Web交互界面，支持API配置、数据库管理、历史记录等功能
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import sqlite3
import tempfile
import threading

# 导入现有的Agent模块
from agent import ReactAgent
from AgentConfig import AgentConfig
from database_tools import DatabaseManager, DatabaseTools

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'llm_auto_agent_web_secret_key_2025'
CORS(app)

# 全局变量
active_agents = {}
user_sessions = {}

class WebAgentManager:
    """Web界面专用的Agent管理器"""
    
    def __init__(self):
        self.agents = {}
        self.user_configs = {}
        
    def create_agent_for_user(self, user_id, api_key, use_database=False, db_config=None):
        """为用户创建Agent实例"""
        try:
            # 创建配置
            config = AgentConfig()
            config.api_key = api_key
            config.use_database = use_database
            
            if use_database and db_config:
                config.database_config = db_config
            
            # 创建Agent
            agent = ReactAgent(config)
            self.agents[user_id] = agent
            self.user_configs[user_id] = {
                'api_key': api_key,
                'use_database': use_database,
                'db_config': db_config
            }
            
            return agent
        except Exception as e:
            logger.error(f"创建Agent失败: {e}")
            raise
    
    def get_agent(self, user_id):
        """获取用户的Agent实例"""
        return self.agents.get(user_id)
    
    def remove_agent(self, user_id):
        """移除用户的Agent实例"""
        if user_id in self.agents:
            del self.agents[user_id]
        if user_id in self.user_configs:
            del self.user_configs[user_id]

agent_manager = WebAgentManager()

# SQLite数据库用于Web界面管理
class WebDatabase:
    """Web界面专用的SQLite数据库"""
    
    def __init__(self, db_path='web_sessions.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建会话表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT,
                api_key TEXT,
                use_database INTEGER,
                db_config TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建对话历史表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                conversation_id TEXT,
                role TEXT,
                content TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES user_sessions (session_id)
            )
        ''')
        
        # 创建知识库表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                title TEXT,
                content TEXT,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES user_sessions (session_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_session(self, session_id, user_id, api_key, use_database, db_config):
        """保存用户会话"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_sessions 
            (session_id, user_id, api_key, use_database, db_config, last_activity)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (session_id, user_id, api_key, use_database, json.dumps(db_config) if db_config else None))
        
        conn.commit()
        conn.close()
    
    def get_session(self, session_id):
        """获取用户会话"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM user_sessions WHERE session_id = ?', (session_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return {
                'session_id': row[0],
                'user_id': row[1],
                'api_key': row[2],
                'use_database': bool(row[3]),
                'db_config': json.loads(row[4]) if row[4] else None
            }
        return None
    
    def save_message(self, session_id, conversation_id, role, content):
        """保存对话消息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversation_history 
            (session_id, conversation_id, role, content)
            VALUES (?, ?, ?, ?)
        ''', (session_id, conversation_id, role, content))
        
        conn.commit()
        conn.close()
    
    def get_conversation_history(self, session_id, conversation_id):
        """获取对话历史"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT role, content, timestamp 
            FROM conversation_history 
            WHERE session_id = ? AND conversation_id = ?
            ORDER BY timestamp ASC
        ''', (session_id, conversation_id))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                'role': row[0],
                'content': row[1],
                'timestamp': row[2]
            })
        
        conn.close()
        return messages
    
    def get_user_conversations(self, session_id):
        """获取用户的所有对话"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT conversation_id, MAX(timestamp) as last_activity
            FROM conversation_history 
            WHERE session_id = ?
            GROUP BY conversation_id
            ORDER BY last_activity DESC
        ''', (session_id,))
        
        conversations = []
        for row in cursor.fetchall():
            conversations.append({
                'conversation_id': row[0],
                'last_activity': row[1]
            })
        
        conn.close()
        return conversations

web_db = WebDatabase()

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/api/initialize', methods=['POST'])
def initialize_agent():
    """初始化Agent"""
    try:
        data = request.json
        api_key = data.get('api_key')
        use_database = data.get('use_database', False)
        db_config = data.get('db_config', {})
        
        if not api_key:
            return jsonify({'error': 'API Key不能为空'}), 400
        
        # 生成用户ID和会话ID
        user_id = f"user_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        session_id = request.cookies.get('session_id') or f"session_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        # 创建Agent
        agent = agent_manager.create_agent_for_user(user_id, api_key, use_database, db_config)
        
        # 保存会话
        web_db.save_session(session_id, user_id, api_key, use_database, db_config)
        
        # 创建新对话
        conversation_id = f"conv_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'session_id': session_id,
            'conversation_id': conversation_id,
            'message': 'Agent初始化成功'
        })
        
    except Exception as e:
        logger.error(f"初始化Agent失败: {e}")
        return jsonify({'error': f'初始化失败: {str(e)}'}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """处理聊天请求"""
    try:
        data = request.json
        user_input = data.get('message')
        user_id = data.get('user_id')
        session_id = data.get('session_id')
        conversation_id = data.get('conversation_id')
        
        if not all([user_input, user_id, session_id, conversation_id]):
            return jsonify({'error': '缺少必要参数'}), 400
        
        # 获取Agent
        agent = agent_manager.get_agent(user_id)
        if not agent:
            return jsonify({'error': 'Agent未初始化，请先配置API Key'}), 400
        
        # 保存用户消息
        web_db.save_message(session_id, conversation_id, 'user', user_input)
        
        # 执行Agent
        def run_agent():
            try:
                result = agent.run(user_input)
                
                # 保存AI回复
                if result and 'final_answer' in result:
                    web_db.save_message(session_id, conversation_id, 'assistant', result['final_answer'])
                
                return result
            except Exception as e:
                logger.error(f"Agent执行失败: {e}")
                error_msg = f"执行失败: {str(e)}"
                web_db.save_message(session_id, conversation_id, 'assistant', error_msg)
                return {'error': error_msg}
        
        # 在新线程中运行Agent以避免阻塞
        thread = threading.Thread(target=run_agent)
        thread.start()
        thread.join(timeout=120)  # 2分钟超时
        
        if thread.is_alive():
            return jsonify({'error': '请求超时，请重试'}), 408
        
        result = run_agent()
        
        if 'error' in result:
            return jsonify(result), 500
        
        return jsonify({
            'success': True,
            'response': result.get('final_answer', '未获取到回复'),
            'reasoning_steps': result.get('reasoning_steps', []),
            'tools_used': result.get('tools_used', [])
        })
        
    except Exception as e:
        logger.error(f"聊天处理失败: {e}")
        return jsonify({'error': f'处理失败: {str(e)}'}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """获取对话历史"""
    try:
        session_id = request.args.get('session_id')
        conversation_id = request.args.get('conversation_id')
        
        if not session_id:
            return jsonify({'error': '缺少session_id'}), 400
        
        if conversation_id:
            # 获取特定对话的历史
            messages = web_db.get_conversation_history(session_id, conversation_id)
            return jsonify({'messages': messages})
        else:
            # 获取用户的所有对话
            conversations = web_db.get_user_conversations(session_id)
            return jsonify({'conversations': conversations})
        
    except Exception as e:
        logger.error(f"获取历史失败: {e}")
        return jsonify({'error': f'获取历史失败: {str(e)}'}), 500

@app.route('/api/new_conversation', methods=['POST'])
def new_conversation():
    """创建新对话"""
    try:
        session_id = request.json.get('session_id')
        
        if not session_id:
            return jsonify({'error': '缺少session_id'}), 400
        
        conversation_id = f"conv_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        return jsonify({
            'success': True,
            'conversation_id': conversation_id,
            'message': '新对话创建成功'
        })
        
    except Exception as e:
        logger.error(f"创建新对话失败: {e}")
        return jsonify({'error': f'创建失败: {str(e)}'}), 500

@app.route('/api/import_knowledge', methods=['POST'])
def import_knowledge():
    """导入知识库"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有上传文件'}), 400
        
        file = request.files['file']
        session_id = request.form.get('session_id')
        
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        # 这里可以添加文件处理逻辑
        # 目前只是简单保存
        filename = file.filename
        
        return jsonify({
            'success': True,
            'message': f'文件 {filename} 上传成功',
            'filename': filename
        })
        
    except Exception as e:
        logger.error(f"导入知识库失败: {e}")
        return jsonify({'error': f'导入失败: {str(e)}'}), 500

@app.route('/api/confirm_command', methods=['POST'])
def confirm_command():
    """确认系统命令执行"""
    try:
        data = request.json
        command = data.get('command')
        confirmed = data.get('confirmed', False)
        
        if not command:
            return jsonify({'error': '缺少命令'}), 400
        
        if not confirmed:
            return jsonify({
                'success': False,
                'requires_confirmation': True,
                'command': command,
                'message': '命令需要确认'
            })
        
        # 这里可以添加命令执行逻辑
        # 注意：实际执行系统命令需要谨慎处理
        
        return jsonify({
            'success': True,
            'message': f'命令已确认: {command}'
        })
        
    except Exception as e:
        logger.error(f"命令确认失败: {e}")
        return jsonify({'error': f'确认失败: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    # 创建必要的目录
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    print("LLM Auto Agent Web 服务启动中...")
    print("访问地址: http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)