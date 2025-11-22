"""
增强版日志系统 - 支持彩色输出、文件轮转、结构化日志
完全向后兼容，不破坏现有代码
"""
import os
import sys
import logging
import colorlog
from datetime import datetime
from pathlib import Path
from typing import Optional


class AgentLogger:
    """智能代理日志记录器"""
    
    def __init__(self, name: str = "LLM_Agent"):
        self.name = name
        self.logger = None
        self._setup_logger()
    
    def _setup_logger(self):
        """设置日志记录器"""
        # 创建日志记录器
        self.logger = logging.getLogger(self.name)
        
        # 如果已经配置过，直接返回
        if self.logger.handlers:
            return
        
        # 设置日志级别
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        self.logger.setLevel(getattr(logging, log_level, logging.INFO))
        
        # 设置日志格式
        console_formatter = colorlog.ColoredFormatter(
            '%(log_color)s[%(asctime)s] %(levelname)-8s %(name)s: %(message)s',
            datefmt='%H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
        
        file_formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)-8s %(name)s [%(filename)s:%(lineno)d]: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # 文件处理器（可选）
        log_file = os.getenv("LOG_FILE", "agent.log")
        if log_file:
            try:
                log_path = Path(log_file)
                log_path.parent.mkdir(parents=True, exist_ok=True)
                
                file_handler = logging.FileHandler(log_path, encoding='utf-8')
                file_handler.setFormatter(file_formatter)
                self.logger.addHandler(file_handler)
            except Exception as e:
                self.logger.warning(f"无法创建文件日志处理器: {e}")
        
        # 防止日志传播到根记录器
        self.logger.propagate = False
    
    def debug(self, msg: str, *args, **kwargs):
        """记录调试信息"""
        self.logger.debug(msg, *args, **kwargs)
    
    def info(self, msg: str, *args, **kwargs):
        """记录信息"""
        self.logger.info(msg, *args, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs):
        """记录警告"""
        self.logger.warning(msg, *args, **kwargs)
    
    def error(self, msg: str, *args, exc_info=False, **kwargs):
        """记录错误"""
        self.logger.error(msg, *args, exc_info=exc_info, **kwargs)
    
    def critical(self, msg: str, *args, **kwargs):
        """记录严重错误"""
        self.logger.critical(msg, *args, **kwargs)
    
    def exception(self, msg: str, *args, **kwargs):
        """记录异常信息"""
        self.logger.exception(msg, *args, **kwargs)
    
    def log_api_call(self, provider: str, model: str, prompt_tokens: int, completion_tokens: int, cost: float = 0.0):
        """记录API调用信息"""
        total_tokens = prompt_tokens + completion_tokens
        self.info(f"API调用 - 提供商: {provider}, 模型: {model}, "
                  f"Tokens: {prompt_tokens}/{completion_tokens}/{total_tokens}, "
                  f"预估成本: ${cost:.6f}")
    
    def log_tool_call(self, tool_name: str, args: dict, success: bool, duration: float):
        """记录工具调用信息"""
        status = "成功" if success else "失败"
        self.debug(f"工具调用 - {tool_name}: {status} (耗时: {duration:.3f}s), 参数: {args}")
    
    def log_conversation(self, role: str, content: str):
        """记录对话信息（调试用）"""
        if os.getenv("LOG_CONVERSATION", "false").lower() == "true":
            content_preview = content[:100] + "..." if len(content) > 100 else content
            self.debug(f"对话 - {role}: {content_preview}")
    
    def log_step(self, step: int, action: str, result: str):
        """记录执行步骤"""
        self.info(f"步骤 {step}: {action}")
        self.debug(f"步骤 {step} 结果: {result[:200]}...")


# 全局日志实例（向后兼容）
logger = AgentLogger("LLM_Agent")


# 简化的日志函数（向后兼容）
def setup_logger(log_file: Optional[str] = None, level: str = "INFO"):
    """简化日志设置（保持向后兼容）"""
    if log_file:
        os.environ["LOG_FILE"] = log_file
    os.environ["LOG_LEVEL"] = level
    global logger
    logger = AgentLogger("LLM_Agent")
    return logger


def get_logger(name: str = None) -> AgentLogger:
    """获取日志记录器实例"""
    if name:
        return AgentLogger(name)
    return logger


# 日志上下文管理器（用于临时改变日志级别）
class LogLevelContext:
    """临时改变日志级别的上下文管理器"""
    
    def __init__(self, level: str):
        self.level = level
        self.original_level = None
    
    def __enter__(self):
        self.original_level = logger.logger.level
        logger.logger.setLevel(getattr(logging, self.level.upper(), logging.INFO))
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.logger.setLevel(self.original_level)


# 性能日志装饰器
def log_performance(func):
    """性能日志装饰器"""
    import functools
    import time
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger.debug(f"开始执行: {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.debug(f"执行完成: {func.__name__} (耗时: {duration:.3f}s)")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"执行失败: {func.__name__} (耗时: {duration:.3f}s), 错误: {e}")
            raise
    
    return wrapper


# 错误计数器（用于跟踪重复错误）
class ErrorCounter:
    """错误计数器，用于跟踪和限制重复错误"""
    
    def __init__(self, max_errors: int = 3):
        self.max_errors = max_errors
        self.errors = {}
    
    def count(self, error_type: str) -> int:
        """记录错误并返回当前计数"""
        if error_type not in self.errors:
            self.errors[error_type] = 0
        self.errors[error_type] += 1
        return self.errors[error_type]
    
    def should_stop(self, error_type: str) -> bool:
        """判断是否应停止执行"""
        return self.errors.get(error_type, 0) >= self.max_errors
    
    def reset(self, error_type: str = None):
        """重置错误计数"""
        if error_type:
            self.errors[error_type] = 0
        else:
            self.errors.clear()
    
    def get_stats(self) -> dict:
        """获取错误统计"""
        return {
            "total_errors": sum(self.errors.values()),
            "error_types": len(self.errors),
            "details": self.errors.copy()
        }


# 全局错误计数器实例
error_counter = ErrorCounter()


if __name__ == "__main__":
    # 测试日志系统
    print("测试日志系统:")
    
    logger.info("这是一条信息日志")
    logger.warning("这是一条警告日志")
    logger.debug("这是一条调试日志")
    
    try:
        raise ValueError("测试异常")
    except Exception as e:
        logger.error("捕获到异常", exc_info=True)
    
    # 测试API调用日志
    logger.log_api_call("deepseek", "deepseek-chat", 100, 200, 0.001)
    
    # 测试工具调用日志
    logger.log_tool_call("search_web", {"query": "test"}, True, 1.5)
    
    # 测试错误计数器
    print("\n测试错误计数器:")
    print(f"错误1计数: {error_counter.count('api_error')}")
    print(f"错误1计数: {error_counter.count('api_error')}")
    print(f"应该停止: {error_counter.should_stop('api_error')}")
    print(f"错误2计数: {error_counter.count('tool_error')}")
    print(f"错误统计: {error_counter.get_stats()}")
    
    # 使用上下文管理器临时改变日志级别
    print("\n测试日志级别上下文:")
    logger.debug("这条应该不显示")
    with LogLevelContext("DEBUG"):
        logger.debug("这条应该显示")
    logger.debug("这条又不显示了")
    
    print("\n日志测试完成！")
