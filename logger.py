"""
日志系统
提供统一的日志记录和管理功能
"""
import logging
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from colorama import Fore, Style, init

init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器"""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.MAGENTA
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{log_color}{record.levelname}{Style.RESET_ALL}"
        return super().format(record)


class LoggerManager:
    """日志管理器"""
    
    def __init__(self, name="LLM_Agent", level=logging.INFO, log_file=None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # 避免重复添加处理器
        if self.logger.handlers:
            return
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        # 格式化器
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # 文件处理器
        if log_file:
            file_handler = RotatingFileHandler(
                log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
    
    def get_logger(self):
        """获取日志记录器"""
        return self.logger
    
    def debug(self, message):
        """调试日志"""
        self.logger.debug(message)
    
    def info(self, message):
        """信息日志"""
        self.logger.info(message)
    
    def warning(self, message):
        """警告日志"""
        self.logger.warning(message)
    
    def error(self, message, exc_info=False):
        """错误日志"""
        self.logger.error(message, exc_info=exc_info)
    
    def critical(self, message, exc_info=False):
        """严重错误日志"""
        self.logger.critical(message, exc_info=exc_info)


# 全局日志实例
logger_manager = LoggerManager()
logger = logger_manager.get_logger()