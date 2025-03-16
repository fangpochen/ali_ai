#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI视频标题改名器命令行界面
通过命令行使用AI改名器对视频标题进行改写
"""

import os
import sys
import argparse
from ai_rename import AIRenamer
from config import (
    BAIDU_API_KEY, BAIDU_SECRET_KEY, 
    ALIYUN_API_KEY, ALIYUN_SECRET_KEY,
    XUNFEI_APP_ID, XUNFEI_API_KEY, XUNFEI_API_SECRET,
    CHATGLM_API_KEY, 
    STYLE_PRESETS, DEFAULT_TEMPERATURE, DEFAULT_MODEL,
    AVAILABLE_MODELS
)

def parse_args():
    """
    解析命令行参数
    
    返回:
        解析后的参数对象
    """
    parser = argparse.ArgumentParser(description='AI视频标题改名器 - 根据原始标题生成新的视频标题')
    
    # 必须参数
    parser.add_argument('title', nargs='?', help='需要重命名的原始标题')
    
    # 可选参数
    parser.add_argument('-f', '--file', help='包含多个标题的文件路径，每行一个标题')
    parser.add_argument('-o', '--output', help='输出结果的文件路径')
    parser.add_argument('-l', '--length', type=int, help='生成标题的目标字数')
    parser.add_argument('-s', '--style', default='default', help='生成标题的风格，如"幽默"、"正式"等')
    parser.add_argument('-t', '--temperature', type=float, default=DEFAULT_TEMPERATURE, help='生成的随机性(0.0-1.0)')
    parser.add_argument('-n', '--num', type=int, default=1, help='每个原始标题生成的变体数量')
    
    # 模型相关参数
    parser.add_argument('-m', '--model', default=DEFAULT_MODEL, choices=list(AVAILABLE_MODELS.keys()), 
                      help='使用的AI模型')
    
    # API密钥参数
    # 百度文心一言API密钥
    parser.add_argument('--baidu-api-key', help='百度文心一言API密钥')
    parser.add_argument('--baidu-secret-key', help='百度文心一言Secret密钥')
    
    # 阿里云通义千问API密钥
    parser.add_argument('--aliyun-api-key', help='阿里云通义千问API密钥')
    parser.add_argument('--aliyun-secret-key', help='阿里云通义千问Secret密钥')
    
    # 讯飞API密钥
    parser.add_argument('--xunfei-app-id', help='讯飞星火APP ID')
    parser.add_argument('--xunfei-api-key', help='讯飞星火API密钥')
    parser.add_argument('--xunfei-api-secret', help='讯飞星火API Secret')
    
    # 智谱API密钥
    parser.add_argument('--chatglm-api-key', help='智谱AI ChatGLM API密钥')
    
    # 其他参数
    parser.add_argument('--list-styles', action='store_true', help='列出所有可用的标题风格预设')
    parser.add_argument('--list-models', action='store_true', help='列出所有可用的AI模型')
    
    return parser.parse_args()

def print_styles():
    """打印所有可用的标题风格预设"""
    print("可用的标题风格预设:")
    for style, description in STYLE_PRESETS.items():
        print(f"  - {style}: {description}")

def print_models():
    """打印所有可用的AI模型"""
    print("可用的AI模型:")
    for model, description in AVAILABLE_MODELS.items():
        print(f"  - {model}: {description}")

def process_single_title(renamer, title, args):
    """
    处理单个标题
    
    参数:
        renamer: AIRenamer实例
        title: 原始标题
        args: 命令行参数
        
    返回:
        生成的新标题(列表或字符串)
    """
    result = renamer.rename(
        title, 
        target_length=args.length, 
        style=args.style,
        temperature=args.temperature,
        num_variants=args.num
    )
    
    # 打印结果
    print(f"原标题: {title}")
    if args.num == 1:
        print(f"新标题: {result}")
    else:
        print("生成的变体:")
        for i, variant in enumerate(result, 1):
            print(f"  {i}. {variant}")
    print()
    
    return result

def process_file(renamer, file_path, args):
    """
    处理包含多个标题的文件
    
    参数:
        renamer: AIRenamer实例
        file_path: 标题文件路径
        args: 命令行参数
        
    返回:
        原始标题和生成标题的列表对
    """
    results = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            titles = [line.strip() for line in f if line.strip()]
        
        print(f"从文件 {file_path} 中读取了 {len(titles)} 个标题")
        
        for i, title in enumerate(titles, 1):
            print(f"\n处理标题 {i}/{len(titles)}")
            new_title = process_single_title(renamer, title, args)
            results.append((title, new_title))
            
    except Exception as e:
        print(f"处理文件时出错: {e}")
        sys.exit(1)
        
    return results

def save_results(results, output_path, args):
    """
    保存结果到文件
    
    参数:
        results: 结果列表
        output_path: 输出文件路径
        args: 命令行参数
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# AI视频标题改名器生成结果\n\n")
            f.write(f"使用模型: {AVAILABLE_MODELS.get(args.model, args.model)}\n\n")
            
            for i, (original, new) in enumerate(results, 1):
                f.write(f"## 标题 {i}\n")
                f.write(f"原标题: {original}\n")
                
                if args.num == 1:
                    f.write(f"新标题: {new}\n")
                else:
                    f.write("生成的变体:\n")
                    for j, variant in enumerate(new, 1):
                        f.write(f"{j}. {variant}\n")
                f.write("\n")
                
        print(f"结果已保存到 {output_path}")
        
    except Exception as e:
        print(f"保存结果时出错: {e}")
        sys.exit(1)

def get_api_keys(args):
    """
    获取API密钥
    
    参数:
        args: 命令行参数
        
    返回:
        api_key: 主API密钥
        secret_key: 辅助密钥(如有需要)
    """
    model = args.model
    api_key = None
    secret_key = None
    
    # 根据模型选择合适的API密钥
    if model in ["ernie_bot", "ernie_bot_turbo"]:
        api_key = args.baidu_api_key or BAIDU_API_KEY or os.environ.get("BAIDU_API_KEY")
        secret_key = args.baidu_secret_key or BAIDU_SECRET_KEY or os.environ.get("BAIDU_SECRET_KEY")
        
        if not api_key or not secret_key:
            print("错误: 使用百度文心一言模型需要提供API密钥和Secret密钥")
            print("请通过--baidu-api-key和--baidu-secret-key参数提供，或在config.py中设置，或设置环境变量")
            sys.exit(1)
            
    elif model in ["qwen", "qwen-turbo", "qwen-plus"]:
        api_key = args.aliyun_api_key or ALIYUN_API_KEY or os.environ.get("ALIYUN_API_KEY")
        secret_key = args.aliyun_secret_key or ALIYUN_SECRET_KEY or os.environ.get("ALIYUN_SECRET_KEY")
        
        if not api_key:
            print("错误: 使用阿里云通义千问模型需要提供API密钥")
            print("请通过--aliyun-api-key参数提供，或在config.py中设置，或设置环境变量")
            sys.exit(1)
            
    elif model == "spark":
        api_key = args.xunfei_api_key or XUNFEI_API_KEY or os.environ.get("XUNFEI_API_KEY")
        if not api_key:
            print("错误: 使用讯飞星火模型需要提供API密钥")
            print("请通过--xunfei-api-key参数提供，或在config.py中设置，或设置环境变量")
            sys.exit(1)
            
    elif model == "chatglm":
        api_key = args.chatglm_api_key or CHATGLM_API_KEY or os.environ.get("CHATGLM_API_KEY")
        if not api_key:
            print("错误: 使用智谱AI ChatGLM模型需要提供API密钥")
            print("请通过--chatglm-api-key参数提供，或在config.py中设置，或设置环境变量")
            sys.exit(1)
    
    return api_key, secret_key

def main():
    """主函数"""
    args = parse_args()
    
    # 显示预设风格列表后退出
    if args.list_styles:
        print_styles()
        return
    
    # 显示可用模型列表后退出
    if args.list_models:
        print_models()
        return
    
    # 获取API密钥
    api_key, secret_key = get_api_keys(args)
    
    # 初始化改名器
    try:
        renamer = AIRenamer(api_key=api_key, secret_key=secret_key, model=args.model)
    except ValueError as e:
        print(f"初始化AI改名器失败: {e}")
        sys.exit(1)
    except NotImplementedError as e:
        print(f"错误: {e}")
        print(f"模型 {args.model} 目前尚未完全实现，请选择其他模型")
        sys.exit(1)
    
    # 处理输入
    results = []
    if args.file:
        # 从文件读取多个标题
        results = process_file(renamer, args.file, args)
    elif args.title:
        # 处理单个标题
        new_title = process_single_title(renamer, args.title, args)
        results = [(args.title, new_title)]
    else:
        print("错误: 请提供标题或包含标题的文件。使用 --help 查看帮助。")
        sys.exit(1)
    
    # 保存结果
    if args.output and results:
        save_results(results, args.output, args)

if __name__ == "__main__":
    main() 