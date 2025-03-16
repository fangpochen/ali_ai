#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文件夹批量重命名工具 - 通义千问版
"""

import os
import time
from openai import OpenAI

def batch_rename_files(folder_path, api_key, batch_size=3):
    """批量重命名文件夹中的文件
    
    参数:
        folder_path: 文件夹路径
        api_key: 通义千问API密钥
        batch_size: 每批处理的文件数量
    """
    # 初始化OpenAI客户端(通义千问兼容模式)
    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    
    # 获取文件夹中的所有文件
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    print(f"找到{len(files)}个文件")
    
    # 批量处理文件
    for i in range(0, len(files), batch_size):
        batch_files = files[i:i+batch_size]
        print(f"\n处理批次 {i//batch_size + 1}/{(len(files)-1)//batch_size + 1}，共{len(batch_files)}个文件:")
        
        # 构建提示
        file_list_text = "\n".join([f"{idx+1}. {file}" for idx, file in enumerate(batch_files)])
        prompt = f"""请帮我优化以下{len(batch_files)}个文件名，生成更加简洁、清晰的新文件名。
保留原文件名的扩展名(.jpg/.mp4等)，保持原意但让文件名更有吸引力。
请按照以下格式返回结果，只需返回编号和新文件名：

原文件列表:
{file_list_text}

新文件名:
1. [新文件名1]
2. [新文件名2]
3. [新文件名3]
"""
        
        try:
            # 调用通义千问API
            response = client.chat.completions.create(
                model="qwen-turbo",  # 使用turbo版本处理速度更快
                messages=[
                    {"role": "system", "content": "你是一个专业的文件重命名助手，擅长生成简洁有吸引力的文件名。"},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # 提取生成的文件名
            content = response.choices[0].message.content
            print("API返回内容:")
            print(content)
            
            # 解析返回的文件名
            new_filenames = []
            lines = content.split('\n')
            for line in lines:
                if line.strip() and line[0].isdigit() and '. ' in line:
                    parts = line.split('. ', 1)
                    if len(parts) == 2 and parts[0].isdigit():
                        idx = int(parts[0]) - 1
                        if 0 <= idx < len(batch_files):
                            new_name = parts[1].strip().strip('[]')
                            if new_name:
                                new_filenames.append((idx, new_name))
            
            # 确认并重命名文件
            if new_filenames:
                print("\n以下文件将被重命名:")
                for idx, new_name in new_filenames:
                    if idx < len(batch_files):
                        old_name = batch_files[idx]
                        # 保留原扩展名
                        _, ext = os.path.splitext(old_name)
                        if not new_name.endswith(ext):
                            new_name = new_name + ext
                        
                        print(f"{old_name} -> {new_name}")
                
                confirm = input("\n确认重命名这些文件? (y/n): ").lower()
                if confirm == 'y':
                    for idx, new_name in new_filenames:
                        if idx < len(batch_files):
                            old_path = os.path.join(folder_path, batch_files[idx])
                            new_path = os.path.join(folder_path, new_name)
                            try:
                                os.rename(old_path, new_path)
                                print(f"已重命名: {batch_files[idx]} -> {new_name}")
                            except Exception as e:
                                print(f"重命名失败: {batch_files[idx]} - {e}")
            else:
                print("无法从API响应中提取有效的文件名")
                
        except Exception as e:
            print(f"处理批次时出错: {e}")
        
        # 避免API限流，添加延迟
        if i + batch_size < len(files):
            delay = 2  # 2秒延迟，避免触发限流
            print(f"\n等待{delay}秒，避免API限流...")
            time.sleep(delay)

if __name__ == "__main__":
    # 用户输入
    folder_path = input("请输入文件夹路径: ")
    api_key = input("请输入通义千问API密钥: ")
    
    # 验证输入
    if not os.path.isdir(folder_path):
        print("错误: 无效的文件夹路径")
    elif not api_key:
        print("错误: 必须提供API密钥")
    else:
        batch_rename_files(folder_path, api_key) 