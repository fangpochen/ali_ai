#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI视频标题改名器演示脚本
演示如何使用AI改名器对视频标题进行改写
"""

import os
from ai_rename import AIRenamer
from config import (
    BAIDU_API_KEY, BAIDU_SECRET_KEY, 
    STYLE_PRESETS, DEFAULT_MODEL,
    AVAILABLE_MODELS
)

def main():
    """主函数，演示AI改名器的使用方法"""
    
    # 选择使用的模型
    model = DEFAULT_MODEL  # 默认使用百度文心一言标准版
    
    # 检查API密钥是否配置
    api_key = BAIDU_API_KEY or os.environ.get("BAIDU_API_KEY")
    secret_key = BAIDU_SECRET_KEY or os.environ.get("BAIDU_SECRET_KEY")
    
    if not api_key or not secret_key:
        print(f"错误: 未配置{AVAILABLE_MODELS.get(model, model)}API密钥。请在config.py中设置或设置相应的环境变量。")
        return
    
    # 初始化改名器
    try:
        renamer = AIRenamer(api_key=api_key, secret_key=secret_key, model=model)
    except Exception as e:
        print(f"初始化改名器失败: {e}")
        return
    
    # 示例标题
    example_titles = [
        "Python入门教程：从零开始学习编程的完整指南",
        "如何在30天内学会弹吉他 - 初学者教程",
        "2023年最值得买的十款智能手机评测",
        "健身小白必看：在家徒手训练全身肌肉的20个动作"
    ]
    
    print("=" * 50)
    print("AI视频标题改名器演示")
    print(f"使用模型: {AVAILABLE_MODELS.get(model, model)}")
    print("=" * 50)
    
    # 演示1: 基本使用
    original_title = example_titles[0]
    print(f"\n示例1: 基本使用\n原标题: {original_title}")
    
    try:
        new_title = renamer.rename(original_title)
        print(f"新标题: {new_title}")
    except Exception as e:
        print(f"生成标题时出错: {e}")
    
    # 演示2: 指定字数
    original_title = example_titles[1]
    print(f"\n示例2: 指定字数\n原标题: {original_title}")
    
    try:
        new_title = renamer.rename(original_title, target_length=15)
        print(f"新标题 (约15字): {new_title}")
    except Exception as e:
        print(f"生成标题时出错: {e}")
    
    # 演示3: 指定风格
    original_title = example_titles[2]
    print(f"\n示例3: 指定风格\n原标题: {original_title}")
    
    try:
        new_title = renamer.rename(original_title, style="疑问式")
        print(f"新标题 (疑问式风格): {new_title}")
    except Exception as e:
        print(f"生成标题时出错: {e}")
    
    # 演示4: 生成多个变体
    original_title = example_titles[3]
    print(f"\n示例4: 生成多个变体\n原标题: {original_title}")
    
    try:
        new_titles = renamer.rename(original_title, num_variants=3)
        print("多个变体标题:")
        for i, title in enumerate(new_titles, 1):
            print(f"  变体{i}: {title}")
    except Exception as e:
        print(f"生成标题时出错: {e}")
    
    # 演示5: 批量处理
    print("\n示例5: 批量处理多个标题")
    print("原标题列表:")
    for i, title in enumerate(example_titles, 1):
        print(f"  {i}. {title}")
    
    try:
        print("\n生成的新标题:")
        new_titles = renamer.batch_rename(example_titles[:2])  # 只处理前两个以节省API调用
        for i, (old, new) in enumerate(zip(example_titles[:2], new_titles), 1):
            print(f"  {i}. 原: {old}")
            print(f"     新: {new}")
            print()
    except Exception as e:
        print(f"批量处理标题时出错: {e}")
    
    # 打印可用的风格预设
    print("\n可用的标题风格预设:")
    for style, description in STYLE_PRESETS.items():
        print(f"  - {style}: {description}")
    
    # 打印可用的模型
    print("\n可用的AI模型:")
    for model_name, description in AVAILABLE_MODELS.items():
        print(f"  - {model_name}: {description}")

if __name__ == "__main__":
    main() 