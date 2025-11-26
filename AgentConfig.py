import os
import logging

class AgentConfig:
    def __init__(self):
        # 数据库配置
        self.enable_database = os.getenv('ENABLE_DATABASE', 'false').lower() == 'true'  # 修复：应该为 'true' 时启用
        self.db_host = os.getenv('DB_HOST', 'localhost')
        self.db_name = os.getenv('DB_NAME', 'llm_agent')
        self.db_user = os.getenv('DB_USER', 'root')
        self.db_password = os.getenv('DB_PASSWORD', '')
        self.db_port = int(os.getenv('DB_PORT', '3306'))
        
        # API 配置
        self.api_provider = os.getenv('API_PROVIDER', 'deepseek')
        self.api_key = os.getenv('DEEPSEEK_API_KEY', '')
        self.api_base_url = os.getenv('API_BASE_URL', 'https://api.deepseek.com')
        self.model_name = os.getenv('MODEL_NAME', 'deepseek-chat')
        
        # 代理配置
        self.max_steps = int(os.getenv('MAX_STEPS', '10'))
        self.enable_cost_tracking = os.getenv('ENABLE_COST_TRACKING', 'true').lower() == 'true'
        
        logging.info(f"数据库功能状态: {'已启用' if self.enable_database else '已禁用'}")