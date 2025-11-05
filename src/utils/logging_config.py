"""
Logging Configuration
日志配置模块
"""

import logging
import os
from datetime import datetime
from pathlib import Path


def setup_logger(name: str = "v5_anti_backflow", log_dir: str = "logs") -> logging.Logger:
    """
    配置日志记录器

    参数:
        name: 日志记录器名称
        log_dir: 日志目录

    返回:
        配置好的日志记录器
    """
    # 创建 logs 目录
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    # 生成日志文件名（带时间戳）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"{name}_{timestamp}.log")

    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # 避免重复添加处理器
    if logger.handlers:
        return logger

    # 文件处理器（详细日志）
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)

    # 控制台处理器（仅 WARNING 及以上）
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)

    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
