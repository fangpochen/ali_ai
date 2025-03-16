#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI视频标题改名器配置文件
在此文件中配置API密钥和其他设置
"""

# API密钥配置
# 直接在此设置API密钥（不推荐在生产环境中这样做）

# 百度文心一言API配置
BAIDU_API_KEY = ""  # 替换为你的百度API密钥
BAIDU_SECRET_KEY = ""  # 替换为你的百度Secret密钥

# 阿里云通义千问API配置
ALIYUN_API_KEY = ""  # 替换为你的阿里云API密钥
ALIYUN_SECRET_KEY = ""  # 替换为你的阿里云Secret密钥

# 讯飞星火API配置
XUNFEI_APP_ID = ""  # 替换为你的讯飞应用ID
XUNFEI_API_KEY = ""  # 替换为你的讯飞API密钥
XUNFEI_API_SECRET = ""  # 替换为你的讯飞API Secret

# 智谱AI ChatGLM API配置
CHATGLM_API_KEY = ""  # 替换为你的智谱API密钥

# 默认AI模型设置
DEFAULT_MODEL = "qwen"  # 使用的模型名称："ernie_bot", "ernie_bot_turbo", "qwen", "qwen-turbo", "qwen-plus", "spark", "chatglm"

# 标题生成设置
DEFAULT_TEMPERATURE = 0.7  # 生成的随机性(0.0-1.0)，越高结果越多样
DEFAULT_STYLE = "default"  # 默认标题风格

# 批处理设置
BATCH_DELAY = 0.5  # 批量处理时的延迟秒数，避免API限流

# 可用模型列表
AVAILABLE_MODELS = {
    # 百度模型
    "ernie_bot": "百度文心一言(标准版)",
    "ernie_bot_turbo": "百度文心一言(快速版)",
    # 阿里模型
    "qwen": "阿里通义千问(标准版)",
    "qwen-turbo": "阿里通义千问(极速版)",
    "qwen-plus": "阿里通义千问(增强版)",
    # 其他模型
    "spark": "讯飞星火认知大模型",
    "chatglm": "智谱AI ChatGLM"
}

# 预设风格列表
STYLE_PRESETS = {
    "幽默": "幽默风趣，让人忍俊不禁",
    "正式": "正式、专业、学术性强",
    "吸引眼球": "引人注目，激发好奇心，适合获取更多点击",
    "简洁": "简洁明了，直奔主题",
    "疑问式": "以问题形式呈现，引发思考",
    "情感化": "带有情感色彩，引起共鸣",
    "故事化": "以讲故事的方式呈现标题",
    "数字化": "在标题中包含数字，提高可信度"
} 