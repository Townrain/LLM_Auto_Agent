"""
API管理器
统一处理多种LLM API调用
"""
import time
import requests
from typing import Dict, Any, List
from retrying import retry
from config_manager import AgentConfig
from logger import logger


class APIManager:
    """API管理器，支持多种LLM提供商"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.request_count = 0
        self.error_count = 0
        self.total_tokens = 0
        
    def get_model_config(self, model_name=None):
        """获取模型配置"""
        return self.config.get_model_config(model_name)
    
    @retry(stop_max_attempt_number=3, wait_fixed=1000)
    def call_api(self, messages: List[Dict[str, str]], model_name=None, **kwargs) -> str:
        """调用LLM API"""
        model_config = self.get_model_config(model_name)
        
        self.request_count += 1
        logger.debug(f"调用API: {model_config.name}, 请求次数: {self.request_count}")
        
        try:
            if model_config.name == "deepseek":
                return self._call_deepseek(messages, model_config, **kwargs)
            elif model_config.name == "openai":
                return self._call_openai(messages, model_config, **kwargs)
            else:
                raise ValueError(f"不支持的模型: {model_config.name}")
        except Exception as e:
            self.error_count += 1
            logger.error(f"API调用失败: {str(e)}", exc_info=True)
            raise
    
    def _call_deepseek(self, messages: List[Dict[str, str]], config, **kwargs) -> str:
        """调用DeepSeek API"""
        headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": config.model_name,
            "messages": messages,
            "max_tokens": kwargs.get('max_tokens', config.max_tokens),
            "temperature": kwargs.get('temperature', config.temperature),
            "stream": False
        }
        
        start_time = time.time()
        response = requests.post(
            f"{config.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        elapsed = time.time() - start_time
        logger.debug(f"DeepSeek API响应时间: {elapsed:.2f}s")
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # 统计token
            usage = result.get("usage", {})
            self.total_tokens += usage.get("total_tokens", 0)
            
            return content
        else:
            raise Exception(f"API调用失败: {response.status_code} - {response.text}")
    
    def _call_openai(self, messages: List[Dict[str, str]], config, **kwargs) -> str:
        """调用OpenAI API"""
        headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": config.model_name,
            "messages": messages,
            "max_tokens": kwargs.get('max_tokens', config.max_tokens),
            "temperature": kwargs.get('temperature', config.temperature)
        }
        
        start_time = time.time()
        response = requests.post(
            f"{config.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        elapsed = time.time() - start_time
        logger.debug(f"OpenAI API响应时间: {elapsed:.2f}s")
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # 统计token
            usage = result.get("usage", {})
            self.total_tokens += usage.get("total_tokens", 0)
            
            return content
        else:
            raise Exception(f"API调用失败: {response.status_code} - {response.text}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取API使用统计"""
        return {
            "request_count": self.request_count,
            "error_count": self.error_count,
            "total_tokens": self.total_tokens,
            "success_rate": (self.request_count - self.error_count) / max(self.request_count, 1) * 100
        }