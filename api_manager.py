"""
增强版API管理器 - 支持多LLM提供商和智能重试
支持的提供商: DeepSeek, OpenAI, Anthropic
"""
import os
import time
import json
import requests
from typing import Dict, List, Any, Optional, Tuple
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log
from dataclasses import dataclass, asdict
import backoff

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = False
except ImportError:
    ANTHROPIC_AVAILABLE = False

from logger import logger


@dataclass
class APICallStats:
    """API调用统计"""
    provider: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost: float = 0.0
    duration: float = 0.0
    success: bool = True
    error: Optional[str] = None


class APIManager:
    """API管理器，支持多提供商"""
    
    # API定价（每1K tokens，单位：美元）
    PRICING = {
        "deepseek": {
            "deepseek-chat": {"input": 0.00014, "output": 0.00028},  # DeepSeek-V2.5
            "deepseek-coder": {"input": 0.00014, "output": 0.00028},
            "deepseek-reasoner": {"input": 0.0014, "output": 0.028},  # DeepSeek-R1
        },
        "openai": {
            "gpt-4o": {"input": 0.005, "output": 0.015},
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        },
        "anthropic": {
            "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015},
            "claude-3-5-haiku-20241022": {"input": 0.0008, "output": 0.004},
            "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
        }
    }
    
    def __init__(self, config):
        self.config = config
        self.provider = config.get('api.default_provider', 'deepseek')
        self.stats = {
            "request_count": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "errors": 0,
            "by_provider": {}
        }
        
        # 初始化各提供商客户端
        self._init_clients()
        
        logger.info(f"API管理器初始化完成，提供商: {self.provider}")
    
    def _init_clients(self):
        """初始化各提供商客户端"""
        # DeepSeek 使用 requests
        self.deepseek_api_key = self.config.get('api.deepseek.api_key', '')
        self.deepseek_base_url = self.config.get('api.deepseek.base_url', 'https://api.deepseek.com')
        
        # OpenAI 客户端
        if OPENAI_AVAILABLE:
            openai_api_key = self.config.get('api.openai.api_key', '')
            if openai_api_key:
                self.openai_client = openai.OpenAI(
                    api_key=openai_api_key,
                    base_url=self.config.get('api.openai.base_url', None)
                )
            else:
                self.openai_client = None
        else:
            self.openai_client = None
        
        # Anthropic 客户端
        if ANTHROPIC_AVAILABLE:
            anthropic_api_key = self.config.get('api.anthropic.api_key', '')
            if anthropic_api_key:
                self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
            else:
                self.anthropic_client = None
        else:
            self.anthropic_client = None
    
    @property
    def model(self) -> str:
        """当前使用的模型"""
        return self.config.default_model
    
    def get_provider_for_model(self, model: str = None) -> str:
        """根据模型名称获取提供商"""
        model = model or self.model
        
        # DeepSeek 模型
        if model.startswith("deepseek"):
            return "deepseek"
        
        # OpenAI 模型
        if model.startswith("gpt") or model.startswith("o1"):
            return "openai"
        
        # Anthropic 模型
        if model.startswith("claude"):
            return "anthropic"
        
        # 默认返回配置中的提供商
        return self.provider
    
    def estimate_cost(self, provider: str, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """估算API调用成本"""
        pricing = self.PRICING.get(provider, {})
        model_pricing = pricing.get(model, {"input": 0, "output": 0})
        
        input_cost = (prompt_tokens / 1000) * model_pricing.get("input", 0)
        output_cost = (completion_tokens / 1000) * model_pricing.get("output", 0)
        
        return input_cost + output_cost
    
    def update_stats(self, stats: APICallStats):
        """更新统计信息"""
        self.stats["request_count"] += 1
        self.stats["total_tokens"] += stats.total_tokens
        self.stats["total_cost"] += stats.cost
        
        if not stats.success:
            self.stats["errors"] += 1
        
        # 按提供商统计
        provider = stats.provider
        if provider not in self.stats["by_provider"]:
            self.stats["by_provider"][provider] = {
                "request_count": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "errors": 0
            }
        
        self.stats["by_provider"][provider]["request_count"] += 1
        self.stats["by_provider"][provider]["total_tokens"] += stats.total_tokens
        self.stats["by_provider"][provider]["total_cost"] += stats.cost
        if not stats.success:
            self.stats["by_provider"][provider]["errors"] += 1
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        success_rate = ((self.stats["request_count"] - self.stats["errors"]) / self.stats["request_count"] * 100) if self.stats["request_count"] > 0 else 0
        
        return {
            "request_count": self.stats["request_count"],
            "total_tokens": self.stats["total_tokens"],
            "total_cost": self.stats["total_cost"],
            "errors": self.stats["errors"],
            "success_rate": round(success_rate, 2),
            "by_provider": self.stats["by_provider"]
        }
    
    def _prepare_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """准备消息格式"""
        prepared = []
        for msg in messages:
            if isinstance(msg, dict) and "role" in msg and "content" in msg:
                prepared.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        return prepared
    
    def call_deepseek(self, messages: List[Dict[str, str]], model: str = None) -> Tuple[str, APICallStats]:
        """调用 DeepSeek API"""
        model = model or self.model
        
        headers = {
            "Authorization": f"Bearer {self.deepseek_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": self._prepare_messages(messages),
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "top_p": self.config.top_p,
            "stream": False
        }
        
        # DeepSeek 的 URL 已经是完整的端点
        url = f"{self.deepseek_base_url.rstrip('/')}/chat/completions"
        
        logger.debug(f"调用 DeepSeek API: {model}")
        response = requests.post(url, headers=headers, json=data, timeout=self.config.timeout)
        response.raise_for_status()
        
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        # 统计信息
        usage = result.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        
        stats = APICallStats(
            provider="deepseek",
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            cost=self.estimate_cost("deepseek", model, prompt_tokens, completion_tokens)
        )
        
        return content, stats
    
    def call_openai(self, messages: List[Dict[str, str]], model: str = None) -> Tuple[str, APICallStats]:
        """调用 OpenAI API"""
        if not OPENAI_AVAILABLE or not self.openai_client:
            raise ValueError("OpenAI 客户端不可用，请安装 openai 包并配置 API 密钥")
        
        model = model or self.model
        
        logger.debug(f"调用 OpenAI API: {model}")
        response = self.openai_client.chat.completions.create(
            model=model,
            messages=self._prepare_messages(messages),
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            top_p=self.config.top_p
        )
        
        content = response.choices[0].message.content
        usage = response.usage
        
        prompt_tokens = usage.prompt_tokens
        completion_tokens = usage.completion_tokens
        
        stats = APICallStats(
            provider="openai",
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=usage.total_tokens,
            cost=self.estimate_cost("openai", model, prompt_tokens, completion_tokens)
        )
        
        return content, stats
    
    def call_anthropic(self, messages: List[Dict[str, str]], model: str = None) -> Tuple[str, APICallStats]:
        """调用 Anthropic API"""
        if not ANTHROPIC_AVAILABLE or not self.anthropic_client:
            raise ValueError("Anthropic 客户端不可用，请安装 anthropic 包并配置 API 密钥")
        
        model = model or self.model
        
        # Anthropic 的消息格式稍有不同
        # 需要分离系统消息和用户消息
        system_msg = None
        user_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                user_messages.append(msg)
        
        logger.debug(f"调用 Anthropic API: {model}")
        
        kwargs = {
            "model": model,
            "messages": user_messages,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "top_p": self.config.top_p
        }
        
        if system_msg:
            kwargs["system"] = system_msg
        
        response = self.anthropic_client.messages.create(**kwargs)
        content = response.content[0].text
        
        usage = response.usage
        prompt_tokens = usage.input_tokens
        completion_tokens = usage.output_tokens
        
        stats = APICallStats(
            provider="anthropic",
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            cost=self.estimate_cost("anthropic", model, prompt_tokens, completion_tokens)
        )
        
        return content, stats
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((requests.exceptions.RequestException, TimeoutError)),
        before_sleep=before_sleep_log(logger.logger, logging.WARNING)
    )
    def call_api(self, messages: List[Dict[str, str]], model: str = None) -> str:
        """
        调用API的主要方法，支持自动重试
        
        Args:
            messages: 消息列表
            model: 模型名称，如果为None则使用默认模型
            
        Returns:
            AI响应内容
            
        Raises:
            Exception: 当所有重试都失败时抛出异常
        """
        if not messages:
            raise ValueError("消息列表不能为空")
        
        model = model or self.model
        provider = self.get_provider_for_model(model)
        
        start_time = time.time()
        stats = None
        
        try:
            logger.info(f"API请求开始 - 提供商: {provider}, 模型: {model}")
            
            if provider == "deepseek":
                content, stats = self.call_deepseek(messages, model)
            elif provider == "openai":
                content, stats = self.call_openai(messages, model)
            elif provider == "anthropic":
                content, stats = self.call_anthropic(messages, model)
            else:
                raise ValueError(f"不支持的提供商: {provider}")
            
            # 更新统计
            stats.duration = time.time() - start_time
            self.update_stats(stats)
            
            # 记录API调用日志
            logger.log_api_call(
                provider=stats.provider,
                model=stats.model,
                prompt_tokens=stats.prompt_tokens,
                completion_tokens=stats.completion_tokens,
                cost=stats.cost
            )
            
            logger.info(f"API请求成功 - 耗时: {stats.duration:.2f}s, "
                       f"Tokens: {stats.total_tokens}, 成本: ${stats.cost:.6f}")
            
            return content
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"API请求失败 - 提供商: {provider}, 模型: {model}, "
                        f"耗时: {duration:.2f}s, 错误: {str(e)}", exc_info=True)
            
            # 记录失败的统计
            if stats is None:
                stats = APICallStats(
                    provider=provider,
                    model=model,
                    success=False,
                    error=str(e),
                    duration=duration
                )
                self.update_stats(stats)
            
            raise
    
    def call_api_stream(self, messages: List[Dict[str, str]], model: str = None):
        """
        流式调用API（实验性功能）
        
        目前仅支持 DeepSeek
        """
        if not messages:
            raise ValueError("消息列表不能为空")
        
        model = model or self.model
        provider = self.get_provider_for_model(model)
        
        if provider != "deepseek":
            raise NotImplementedError(f"流式响应暂不支持提供商: {provider}")
        
        logger.info(f"开始流式API请求 - 提供商: {provider}, 模型: {model}")
        
        headers = {
            "Authorization": f"Bearer {self.deepseek_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": self._prepare_messages(messages),
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "top_p": self.config.top_p,
            "stream": True
        }
        
        url = f"{self.deepseek_base_url.rstrip('/')}/chat/completions"
        
        response = requests.post(url, headers=headers, json=data, timeout=self.config.timeout, stream=True)
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                        if "choices" in chunk and len(chunk["choices"]) > 0:
                            delta = chunk["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
                    except json.JSONDecodeError:
                        continue


# 向后兼容的函数
def call_deepseek_api(messages, api_key=None, base_url=None, model="deepseek-chat",
                     max_tokens=4000, temperature=0.7):
    """向后兼容的 DeepSeek API 调用函数"""
    from config_manager import ConfigManager
    
    config = ConfigManager()
    if api_key:
        config.set('api.deepseek.api_key', api_key)
    if base_url:
        config.set('api.deepseek.base_url', base_url)
    if model:
        config.set('api.deepseek.default_model', model)
    
    api_manager = APIManager(config)
    return api_manager.call_api(messages, model)


if __name__ == "__main__":
    # 测试API管理器
    from config_manager import ConfigManager
    
    config = ConfigManager()
    
    # 检查API密钥
    if not config.deepseek_api_key or config.deepseek_api_key == "your-deepseek-api-key-here":
        print("错误: 请设置 DEEPSEEK_API_KEY 环境变量")
        exit(1)
    
    api_manager = APIManager(config)
    
    # 测试简单对话
    messages = [
        {"role": "user", "content": "你好，请介绍一下你自己"}
    ]
    
    try:
        print("测试API调用...")
        response = api_manager.call_api(messages)
        print(f"\n响应: {response}")
        
        # 打印统计
        stats = api_manager.get_stats()
        print(f"\n统计: {json.dumps(stats, indent=2)}")
        
    except Exception as e:
        print(f"API调用失败: {e}")
