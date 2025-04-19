"""
密钥验证模块
处理软件的密钥验证功能
"""
import os
import platform
import socket
import uuid
import logging
import requests
import cpuinfo
import sys
import json
import time  # 添加导入time模块
from pathlib import Path

# 创建日志目录
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)

# 配置日志
logger = logging.getLogger('key_verification')
logger.setLevel(logging.DEBUG)  # 设置为DEBUG级别以获取更多信息

# 添加文件处理器
file_handler = logging.FileHandler(log_dir / 'key_verification.log')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# 添加控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

import netifaces

# 定义配置类
class Config:
    """配置类，用于管理软件配置和密钥缓存"""
    
    def __init__(self):
        """初始化配置"""
        self.config_dir = Path('config')
        self.config_file = self.config_dir / 'config.json'
        self.key_cache_file = self.config_dir / 'key_cache.json'
        
        # 确保配置目录存在
        self.config_dir.mkdir(exist_ok=True)
        
        # 加载配置
        self.config = self._load_config()
        
    def _load_config(self):
        """加载配置"""
        # 默认配置
        default_config = {
            "api": {
                "base_url": "https://api.cloudoption.site"
            }
        }
        
        # 如果配置文件存在，加载它
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return config
            except Exception as e:
                logger.error(f"加载配置文件出错: {e}")
        
        # 保存默认配置
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2)
        except Exception as e:
            logger.error(f"保存默认配置出错: {e}")
        
        return default_config
    
    def get(self, key, default=None):
        """获取配置值"""
        parts = key.split('.')
        value = self.config
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
        
        return value
    
    def get_cached_key(self):
        """获取缓存的密钥"""
        if not self.key_cache_file.exists():
            return None
        
        try:
            with open(self.key_cache_file, 'r', encoding='utf-8') as f:
                cache = json.load(f)
            
            # 检查缓存是否过期
            if cache.get('expire_time', 0) < time.time():
                return None
            
            return cache.get('key')
        except Exception as e:
            logger.error(f"获取缓存密钥出错: {e}")
            return None
    
    def cache_verified_key(self, key):
        """缓存验证通过的密钥"""
        cache = {
            'key': key,
            'expire_time': time.time() + (7 * 24 * 60 * 60)  # 7天后过期
        }
        
        try:
            with open(self.key_cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache, f, indent=2)
        except Exception as e:
            logger.error(f"缓存密钥出错: {e}")
    
    def clear_key_cache(self):
        """清除密钥缓存"""
        if self.key_cache_file.exists():
            try:
                os.remove(self.key_cache_file)
            except Exception as e:
                logger.error(f"清除密钥缓存出错: {e}")

def get_physical_mac():
    """获取物理MAC地址"""
    for iface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(iface)
        if netifaces.AF_LINK in addrs and not iface.startswith(('lo', 'virbr', 'docker')):
            mac = addrs[netifaces.AF_LINK][0]['addr']
            if mac != "00:00:00:00:00:00":
                return mac
    return None

def verify_key(api_key: str, is_background: bool = False, item: str = "ali_qwen") -> bool:
    """
    验证密钥 (当前版本直接返回验证成功)
    
    Args:
        api_key: 密钥字符串
        is_background: 是否为后台验证
        item: 项目标识，默认为"ali_qwen"
        
    Returns:
        bool: 验证是否成功
    """
    # 简单记录日志但总是返回验证成功
    logger.info(f"验证请求 (自动验证通过模式): {api_key[:4]}***{api_key[-4:] if len(api_key)>8 else ''}")
    return True