"""
增强版配置管理器 - 支持 YAML、环境变量、多层配置
保持向后兼容性
"""
import os
import json
import yaml
from typing import Dict, Any, Optional, Union
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class ConfigManager:
    """增强版配置管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.config_data = {}
        
        # 加载默认配置
        self._load_default_config()
        
        # 加载文件配置
        if config_path and os.path.exists(config_path):
            self._load_config_file(config_path)
        
        # 加载环境变量（环境变量优先级最高）
        self._load_env_overrides()
    
    def _load_default_config(self):
        """加载默认配置"""
        self.config_data = {
            "api": {
                "deepseek": {
                    "api_key": os.getenv("DEEPSEEK_API_KEY", "your-deepseek-api-key-here"),
                    "base_url": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
                    "default_model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
                },
                "openai": {
                    "api_key": os.getenv("OPENAI_API_KEY", ""),
                    "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
                    "default_model": os.getenv("OPENAI_MODEL", "gpt-4o-mini")
                },
                "anthropic": {
                    "api_key": os.getenv("ANTHROPIC_API_KEY", ""),
                    "default_model": os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
                },
                "default_provider": os.getenv("LLM_PROVIDER", "deepseek")  # deepseek, openai, anthropic
            },
            "max_tokens": int(os.getenv("MAX_TOKENS", "4000")),
            "temperature": float(os.getenv("TEMPERATURE", "0.7")),
            "top_p": float(os.getenv("TOP_P", "0.95")),
            "max_steps": int(os.getenv("MAX_STEPS", "20")),
            "timeout": int(os.getenv("TIMEOUT", "60")),
            "retry_attempts": int(os.getenv("RETRY_ATTEMPTS", "3")),
            "retry_delay": int(os.getenv("RETRY_DELAY", "1")),
            
            "database": {
                "enabled": os.getenv("DATABASE_ENABLED", "false").lower() == "true",
                "type": os.getenv("DATABASE_TYPE", "mysql"),
                "host": os.getenv("DB_HOST", "localhost"),
                "port": int(os.getenv("DB_PORT", "3306")),
                "user": os.getenv("DB_USER", "root"),
                "password": os.getenv("DB_PASSWORD", "123456"),
                "database": os.getenv("DB_NAME", "llm_agent_db")
            },
            
            "logging": {
                "level": os.getenv("LOG_LEVEL", "INFO"),
                "file": os.getenv("LOG_FILE", "agent.log"),
                "max_size": os.getenv("LOG_MAX_SIZE", "10MB"),
                "backup_count": int(os.getenv("LOG_BACKUP_COUNT", "5"))
            },
            
            "security": {
                "enable_sandbox": os.getenv("ENABLE_SANDBOX", "true").lower() == "true",
                "allowed_commands": os.getenv("ALLOWED_COMMANDS", "ls,pwd,cd,cat,find,grep,which,python,python3").split(","),
                "blocked_commands": os.getenv("BLOCKED_COMMANDS", "rm -rf,dd,mkfs,shutdown,reboot").split(","),
                "max_command_length": int(os.getenv("MAX_COMMAND_LENGTH", "1000")),
                "enable_code_execution": os.getenv("ENABLE_CODE_EXECUTION", "true").lower() == "true"
            },
            
            "conversation": {
                "max_history": int(os.getenv("MAX_HISTORY", "10")),
                "context_window": int(os.getenv("CONTEXT_WINDOW", "8000")),
                "auto_refresh_prompt": os.getenv("AUTO_REFRESH_PROMPT", "true").lower() == "true",
                "refresh_threshold": int(os.getenv("REFRESH_THRESHOLD", "5"))
            },
            
            "tools": {
                "search_timeout": int(os.getenv("SEARCH_TIMEOUT", "10")),
                "file_size_limit": int(os.getenv("FILE_SIZE_LIMIT", "10485760")),  # 10MB
                "enable_web_search": os.getenv("ENABLE_WEB_SEARCH", "true").lower() == "true",
                "enable_file_operations": os.getenv("ENABLE_FILE_OPERATIONS", "true").lower() == "true"
            }
        }
    
    def _load_config_file(self, config_path: str):
        """从配置文件加载"""
        try:
            path = Path(config_path)
            
            if path.suffix.lower() in ['.yaml', '.yml']:
                with open(path, 'r', encoding='utf-8') as f:
                    file_config = yaml.safe_load(f)
            else:
                with open(path, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
            
            # 合并配置
            self._deep_merge(self.config_data, file_config)
            print(f"配置已加载: {config_path}")
            
        except Exception as e:
            print(f"警告: 加载配置文件失败 {config_path}: {e}")
    
    def _load_env_overrides(self):
        """从环境变量加载覆盖配置"""
        # API配置
        self._set_if_env_exists("LLM_PROVIDER", ["api", "default_provider"])
        self._set_if_env_exists("MAX_TOKENS", ["max_tokens"], int)
        self._set_if_env_exists("TEMPERATURE", ["temperature"], float)
        self._set_if_env_exists("MAX_STEPS", ["max_steps"], int)
        self._set_if_env_exists("TIMEOUT", ["timeout"], int)
        
        # 数据库配置
        self._set_if_env_exists("DATABASE_ENABLED", ["database", "enabled"], lambda x: x.lower() == "true")
        
        # 日志配置
        self._set_if_env_exists("LOG_LEVEL", ["logging", "level"])
        
        # 安全配置
        self._set_if_env_exists("ENABLE_SANDBOX", ["security", "enable_sandbox"], lambda x: x.lower() == "true")
    
    def _set_if_env_exists(self, env_key: str, config_path: list, converter=None):
        """如果环境变量存在则设置配置"""
        value = os.getenv(env_key)
        if value is not None:
            if converter:
                value = converter(value)
            
            # 遍历配置路径
            current = self.config_data
            for key in config_path[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            current[config_path[-1]] = value
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]):
        """深度合并字典"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值，支持点号分隔的键"""
        try:
            keys = key.split('.')
            value = self.config_data
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split('.')
        current = self.config_data
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value
    
    @property
    def deepseek_api_key(self) -> str:
        """DeepSeek API密钥"""
        return self.get('api.deepseek.api_key', '')
    
    @property
    def openai_api_key(self) -> str:
        """OpenAI API密钥"""
        return self.get('api.openai.api_key', '')
    
    @property
    def anthropic_api_key(self) -> str:
        """Anthropic API密钥"""
        return self.get('api.anthropic.api_key', '')
    
    @property
    def default_model(self) -> str:
        """默认模型"""
        provider = self.get('api.default_provider', 'deepseek')
        return self.get(f'api.{provider}.default_model', 'deepseek-chat')
    
    @property
    def base_url(self) -> str:
        """API基础URL"""
        provider = self.get('api.default_provider', 'deepseek')
        # DeepSeek 的 base_url 是完整的 API 端点
        if provider == 'deepseek':
            return self.get(f'api.{provider}.base_url', 'https://api.deepseek.com')
        # 其他提供商可能需要额外的路径
        return self.get(f'api.{provider}.base_url', '')
    
    @property
    def max_tokens(self) -> int:
        """最大token数"""
        return self.get('max_tokens', 4000)
    
    @property
    def temperature(self) -> float:
        """温度参数"""
        return self.get('temperature', 0.7)
    
    @property
    def max_steps(self) -> int:
        """最大步骤数"""
        return self.get('max_steps', 20)
    
    @property
    def timeout(self) -> int:
        """请求超时时间"""
        return self.get('timeout', 60)
    
    @property
    def retry_attempts(self) -> int:
        """重试次数"""
        return self.get('retry_attempts', 3)
    
    def save_to_file(self, config_path: str):
        """保存配置到文件"""
        try:
            path = Path(config_path)
            with open(path, 'w', encoding='utf-8') as f:
                if path.suffix.lower() in ['.yaml', '.yml']:
                    yaml.dump(self.config_data, f, default_flow_style=False, allow_unicode=True)
                else:
                    json.dump(self.config_data, f, indent=2, ensure_ascii=False)
            print(f"配置已保存到: {config_path}")
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"Config(provider={self.get('api.default_provider')}, model={self.default_model})"


# 向后兼容的 AgentConfig 类
class AgentConfig(ConfigManager):
    """保持向后兼容的旧配置类"""
    
    def __init__(self):
        super().__init__(None)
    
    @property
    def MODEL(self) -> str:
        """保持向后兼容"""
        return self.default_model
    
    @property
    def API_KEY(self) -> str:
        """保持向后兼容"""
        return self.deepseek_api_key
    
    @property
    def BASE_URL(self) -> str:
        """保持向后兼容"""
        return self.base_url
    
    @property
    def DATABASE_CONFIG(self) -> Dict[str, Any]:
        """保持向后兼容"""
        return {
            'host': self.get('database.host'),
            'user': self.get('database.user'),
            'password': self.get('database.password'),
            'database': self.get('database.database')
        }


# 配置文件示例
CONFIG_EXAMPLE = """
# LLM Auto Agent 配置文件示例
# 支持 YAML 和 JSON 格式

api:
  default_provider: "deepseek"  # 可选: deepseek, openai, anthropic
  
  deepseek:
    api_key: "your-deepseek-api-key-here"
    base_url: "https://api.deepseek.com"
    default_model: "deepseek-chat"
  
  openai:
    api_key: "your-openai-api-key-here"
    base_url: "https://api.openai.com/v1"
    default_model: "gpt-4o-mini"
  
  anthropic:
    api_key: "your-anthropic-api-key-here"
    default_model: "claude-3-5-sonnet-20241022"

# 模型参数
max_tokens: 4000
temperature: 0.7
top_p: 0.95

# 执行限制
max_steps: 20
timeout: 60
retry_attempts: 3
retry_delay: 1

# 数据库配置
database:
  enabled: false
  type: "mysql"
  host: "localhost"
  port: 3306
  user: "root"
  password: "123456"
  database: "llm_agent_db"

# 日志配置
logging:
  level: "INFO"
  file: "agent.log"
  max_size: "10MB"
  backup_count: 5

# 安全配置
security:
  enable_sandbox: true
  allowed_commands: ["ls", "pwd", "cd", "cat", "find", "grep", "which", "python", "python3"]
  blocked_commands: ["rm -rf", "dd", "mkfs", "shutdown", "reboot"]
  max_command_length: 1000
  enable_code_execution: true

# 对话配置
conversation:
  max_history: 10
  context_window: 8000
  auto_refresh_prompt: true
  refresh_threshold: 5

# 工具配置
tools:
  search_timeout: 10
  file_size_limit: 10485760  # 10MB
  enable_web_search: true
  enable_file_operations: true
"""


if __name__ == "__main__":
    # 测试配置管理器
    config = ConfigManager()
    
    print("默认配置:")
    print(f"  Provider: {config.get('api.default_provider')}")
    print(f"  Model: {config.default_model}")
    print(f"  Max Steps: {config.max_steps}")
    print(f"  Timeout: {config.timeout}s")
    
    # 测试保存配置
    # config.save_to_file("config.yaml")