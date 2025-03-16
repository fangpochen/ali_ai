#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文件夹批量重命名工具GUI版 - 通义千问版
"""

import os
import time
import threading
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
from openai import OpenAI
import traceback  # 添加这一行到文件顶部的导入部分
import httpx  # 添加httpx导入
import datetime  # 导入日期模块

class BatchRenameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("通义千问文件批量重命名工具")
        self.root.geometry("700x600")
        self.root.minsize(650, 500)
        
        # 检查截止日期
        self.check_expiration()
        
        # 创建变量
        self.folder_path_var = tk.StringVar()
        self.api_key_var = tk.StringVar()
        self.batch_size_var = tk.IntVar(value=3)
        self.show_key_var = tk.BooleanVar(value=False)
        self.model_var = tk.StringVar(value="qwen-turbo")
        
        # 创建界面
        self.create_widgets()
        
        # 初始化标志
        self.is_processing = False
    
    def check_expiration(self):
        """检查软件是否过期"""
        today = datetime.datetime.now().date()
        expiration_date = datetime.date(2025, 3, 31)
        
        # 添加日期输出，帮助诊断问题
        print(f"当前系统日期: {today}, 截止日期: {expiration_date}")
        
        # 修改日期比较逻辑，确保只有严格超过截止日期才过期
        if today > expiration_date:
            messagebox.showerror("软件已过期", "本软件试用期已结束，请联系开发者获取最新版本。")
            self.root.destroy()
            exit(0)
        else:
            days_left = (expiration_date - today).days
            print(f"剩余试用天数: {days_left}天")
            
            # 只在剩余天数少于7天时才显示提醒
            if 0 < days_left <= 7:  # 修改为严格小于7天但大于0天
                messagebox.showwarning("试用期即将结束", f"软件试用期还剩{days_left}天，将于2024年3月31日停止使用。")
            # 添加当天到期的提醒
            elif days_left == 0:
                messagebox.showwarning("试用期到期", "软件试用期今天到期，请抓紧使用。")
                
            # 确保任何情况下，只要没超过截止日期，都能正常使用
    
    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 输入区域
        input_frame = ttk.LabelFrame(main_frame, text="配置", padding=5)
        input_frame.pack(fill=tk.X, pady=5)
        
        # 文件夹路径
        ttk.Label(input_frame, text="文件夹路径:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(input_frame, textvariable=self.folder_path_var, width=50).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Button(input_frame, text="浏览...", command=self.browse_folder).grid(row=0, column=2, padx=5, pady=5)
        
        # API密钥
        ttk.Label(input_frame, text="API密钥:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.api_key_entry = ttk.Entry(input_frame, textvariable=self.api_key_var, width=50, show="*")
        self.api_key_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Checkbutton(input_frame, text="显示", variable=self.show_key_var, command=self.toggle_key_visibility).grid(row=1, column=2, padx=5, pady=5)
        
        # 高级设置
        settings_frame = ttk.LabelFrame(main_frame, text="高级设置", padding=5)
        settings_frame.pack(fill=tk.X, pady=5)
        
        # 模型选择
        ttk.Label(settings_frame, text="模型:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        models = ["qwen-turbo", "qwen-plus", "qwen-v1"]
        model_combo = ttk.Combobox(settings_frame, textvariable=self.model_var, values=models, width=15)
        model_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 批量大小
        ttk.Label(settings_frame, text="每批文件数:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        batch_spinbox = ttk.Spinbox(settings_frame, from_=1, to=10, textvariable=self.batch_size_var, width=5)
        batch_spinbox.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        # 操作按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="开始处理", command=self.start_processing)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="停止", command=self.stop_processing, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, variable=self.progress_var, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=5)
        
        # 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="处理日志", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 清除日志按钮
        ttk.Button(log_frame, text="清除日志", command=lambda: self.log_text.delete(1.0, tk.END)).pack(anchor=tk.E, padx=5, pady=5)
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=2)
    
    def browse_folder(self):
        """打开文件夹选择对话框"""
        folder_path = filedialog.askdirectory(title="选择文件夹")
        if folder_path:
            self.folder_path_var.set(folder_path)
    
    def toggle_key_visibility(self):
        """切换API密钥显示/隐藏"""
        if self.show_key_var.get():
            self.api_key_entry.config(show="")
        else:
            self.api_key_entry.config(show="*")
    
    def log(self, message):
        """添加消息到日志区域"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)  # 滚动到底部
        self.root.update_idletasks()
    
    def start_processing(self):
        """开始处理文件"""
        # 验证输入
        folder_path = self.folder_path_var.get().strip()
        api_key = self.api_key_var.get().strip()
        
        if not folder_path or not os.path.isdir(folder_path):
            messagebox.showerror("错误", "请输入有效的文件夹路径")
            return
        
        if not api_key:
            messagebox.showerror("错误", "请输入API密钥")
            return
        
        # 更新UI状态
        self.is_processing = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("正在处理...")
        self.progress.start()
        
        # 在新线程中执行处理，避免界面卡死
        thread = threading.Thread(target=self.process_files, args=(folder_path, api_key))
        thread.daemon = True
        thread.start()
    
    def stop_processing(self):
        """停止处理文件"""
        self.is_processing = False
        self.status_var.set("用户已停止处理")
        self.log("用户已停止处理")
        
        # 更新UI状态
        self.stop_button.config(state=tk.DISABLED)
        self.start_button.config(state=tk.NORMAL)
        self.progress.stop()
    
    def process_files(self, folder_path, api_key):
        """处理文件的线程函数"""
        try:
            batch_size = self.batch_size_var.get()
            model = self.model_var.get()
            
            # 清除可能导致问题的环境变量
            if "SSL_CERT_FILE" in os.environ:
                self.log(f"发现SSL_CERT_FILE环境变量：{os.environ['SSL_CERT_FILE']}")
                del os.environ["SSL_CERT_FILE"]
                self.log("已清除SSL_CERT_FILE环境变量")
                
            if "REQUESTS_CA_BUNDLE" in os.environ:
                self.log(f"发现REQUESTS_CA_BUNDLE环境变量：{os.environ['REQUESTS_CA_BUNDLE']}")
                del os.environ["REQUESTS_CA_BUNDLE"]
                self.log("已清除REQUESTS_CA_BUNDLE环境变量")
                
            # 初始化OpenAI客户端(通义千问兼容模式) - 禁用SSL验证
            try:
                self.log(f"尝试初始化API客户端 - 模型: {model}, API密钥: {'*'*(len(api_key)-4) + api_key[-4:]}")
                self.log("SSL验证已禁用")
                
                # 使用httpx客户端并禁用SSL验证
                client = OpenAI(
                    api_key=api_key,
                    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                    http_client=httpx.Client(verify=False)  # 禁用SSL验证
                )
                self.log("API客户端初始化成功")
            except Exception as e:
                # 输出完整的错误堆栈
                self.log(f"初始化API客户端失败: {e}")
                self.log(traceback.format_exc())
                raise
            
            # 获取文件夹中的所有文件
            files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
            self.log(f"找到{len(files)}个文件")
            
            # 设置进度条最大值
            total_batches = (len(files) - 1) // batch_size + 1
            self.root.after(0, lambda: self.progress.config(mode='determinate', maximum=total_batches))
            self.progress_var.set(0)
            
            # 批量处理文件
            for i in range(0, len(files), batch_size):
                if not self.is_processing:
                    break
                    
                batch_files = files[i:i+batch_size]
                batch_num = i // batch_size + 1
                self.log(f"\n处理批次 {batch_num}/{total_batches}，共{len(batch_files)}个文件:")
                
                # 更新进度条
                self.root.after(0, lambda v=batch_num: self.progress_var.set(v))
                
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
                    self.log("正在请求通义千问API...")
                    response = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": "你是一个专业的文件重命名助手，擅长生成简洁有吸引力的文件名。"},
                            {"role": "user", "content": prompt}
                        ]
                    )
                    
                    # 提取生成的文件名
                    content = response.choices[0].message.content
                    self.log("\nAPI返回内容:")
                    self.log(content)
                    
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
                    
                    # 直接执行重命名操作，不显示确认对话框
                    if new_filenames and self.is_processing:
                        self.log("\n开始执行重命名操作:")
                        for idx, new_name in new_filenames:
                            if not self.is_processing:
                                break
                                
                            old_name = batch_files[idx]
                            # 保留原扩展名
                            _, ext = os.path.splitext(old_name)
                            if not new_name.endswith(ext):
                                new_name = new_name + ext
                            
                            self.log(f"准备重命名: {old_name} -> {new_name}")
                            old_path = os.path.join(folder_path, old_name)
                            new_path = os.path.join(folder_path, new_name)
                            try:
                                os.rename(old_path, new_path)
                                self.log(f"已重命名: {old_name} -> {new_name}")
                            except Exception as e:
                                self.log(f"重命名失败: {old_name} - {e}")
                    else:
                        self.log("无法从API响应中提取有效的文件名")
                        
                except Exception as e:
                    self.log(f"处理批次时出错: {str(e)}")
                    self.log(traceback.format_exc())  # 添加错误堆栈以便调试
                
                # 避免API限流，添加延迟
                if i + batch_size < len(files) and self.is_processing:
                    delay = 2  # 2秒延迟
                    self.log(f"\n等待{delay}秒，避免API限流...")
                    time.sleep(delay)
            
            # 完成处理
            if self.is_processing:
                self.log("\n所有文件处理完成!")
                self.status_var.set("处理完成")
            
        except Exception as e:
            self.log(f"发生错误: {str(e)}")
            self.status_var.set("处理过程中发生错误")
        
        # 恢复UI状态
        self.is_processing = False
        self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.stop_button.config(state=tk.DISABLED))
        self.root.after(0, lambda: self.progress.stop())

def main():
    """主函数"""
    root = tk.Tk()
    app = BatchRenameGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 