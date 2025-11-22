"""
Agent配置管理系统
支持多LLM提供商、环境变量、动态配置
"""
import os
import json
import logging
from typing import Dict, Any, Optional


class ModelConfig:
    """模型配置类"""
    def __init__(self, name, api_key, base_url, model_name, max_tokens=4096, temperature=0.7):
        self.name = name
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature


class DatabaseConfig:
    """数据库配置类"""
    def __init__(self):
        self.enabled = False
        self.host = "localhost"
        self.database = "llm_agent"
        self.user = "root"
        self.password = ""
        self.port = 3306


class AgentConfig:
    """主配置类"""
    
    def __init__(self):
        self.default_model = "deepseek"
        self.models = {}
        self.max_steps = 15
        self.refresh_prompt_interval = 3
        self.database = DatabaseConfig()
        self.project_directory = os.path.expanduser("~/llm_agent_workspace")
        self.conda_env = "base"
        self.enable_database = False
        self.debug_mode = False
        self.show_system_messages = False
        
        self._load_env_config()
        self._validate_config()
    
    def _load_env_config(self):
        """从环境变量加载配置"""
        deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        if deepseek_key:
            self.models["deepseek"] = ModelConfig(
                name="deepseek",
                api_key=deepseek_key,
                base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
                model_name=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
                max_tokens=int(os.getenv("DEEPSEEK_MAX_TOKENS", "4096")),
                temperature=float(os.getenv("DEEPSEEK_TEMPERATURE", "0.7"))
            )
        
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.models["openai"] = ModelConfig(
                name="openai",
                api_key=openai_key,
                base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
                model_name=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "4096")),
                temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
            )
        
        self.database.enabled = os.getenv('ENABLE_DATABASE', 'false').lower() == 'true'
        if self.database.enabled:
            self.database.host = os.getenv('DB_HOST', 'localhost')
            self.database.database = os.getenv('DB_NAME', 'llm_agent')
            self.database.user = os.getenv('DB_USER', 'root')
            self.database.password = os.getenv('DB_PASSWORD', '')
            self.database.port = int(os.getenv('DB_PORT', '3306'))
        
        self.max_steps = int(os.getenv('MAX_STEPS', str(self.max_steps)))
        self.refresh_prompt_interval = int(os.getenv('REFRESH_INTERVAL', str(self.refresh_prompt_interval)))
        self.debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        self.show_system_messages = os.getenv('SHOW_SYSTEM_MESSAGES', 'false').lower() == 'true'
        self.project_directory = os.getenv('PROJECT_DIR', self.project_directory)
        self.conda_env = os.getenv('CONDA_ENV', self.conda_env)
        
        os.makedirs(self.project_directory, exist_ok=True)
    
    def _validate_config(self):
        """验证配置有效性"""
        if self.default_model not in self.models:
            available = list(self.models.keys())
            if available:
                self.default_model = available[0]
    
    def get_model_config(self, model_name=None):
        """获取指定模型的配置"""
        name = model_name or self.default_model
        if name not in self.models:
            raise ValueError(f"模型 '{name}' 未配置")
        return self.models[name]