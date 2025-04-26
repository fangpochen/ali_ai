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
import sys  # 添加sys模块导入
import json  # 添加json模块导入
from pathlib import Path  # 添加pathlib模块导入

# 添加app目录到导入路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 导入密钥验证模块
try:
    from key_verifier import verify_key
    has_key_verifier = True
    print("成功导入密钥验证模块")
except ImportError:
    # 如果找不到模块，定义一个简单的验证函数（始终返回True）
    print("无法导入密钥验证模块，使用本地验证函数")
    has_key_verifier = False
    
    def verify_key(key):
        """本地验证函数，当找不到密钥验证模块时使用"""
        valid_keys = ["QWEN-BATCH-RENAME-KEY-2024", "WEIXIN-DATA-COLLECTOR-KEY-2024", "BATCH-RENAME-PREMIUM-KEY-2024"]
        return key in valid_keys

def show_license_dialog():
    """显示许可证验证对话框，返回验证结果和密钥"""
    # 创建一个专用的Tk窗口
    dialog_root = tk.Tk()
    dialog_root.title("许可证验证")
    dialog_root.geometry("400x200")
    dialog_root.resizable(False, False)
    
    # 验证结果
    result = {'valid': False, 'key': ''}
    
    # 居中显示
    dialog_root.update_idletasks()
    width = dialog_root.winfo_width()
    height = dialog_root.winfo_height()
    screen_width = dialog_root.winfo_screenwidth()
    screen_height = dialog_root.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    dialog_root.geometry(f"{width}x{height}+{x}+{y}")
    
    # 创建变量
    license_key_var = tk.StringVar()
    show_key_var = tk.BooleanVar(value=False)
    status_var = tk.StringVar(value="")
    
    def toggle_key_visibility():
        """切换密钥显示/隐藏"""
        if show_key_var.get():
            license_key_entry.config(show="")
        else:
            license_key_entry.config(show="*")
    
    def verify_license():
        """验证许可证"""
        nonlocal result
        key = license_key_var.get().strip()
        
        if not key:
            status_var.set("请输入许可证密钥")
            return
        
        verify_button.config(state=tk.DISABLED)
        status_var.set("正在验证...")
        dialog_root.update_idletasks()
        
        try:
            # 调用验证函数
            valid = verify_key(key)
            
            if valid:
                # 验证成功
                result['valid'] = True
                result['key'] = key
                dialog_root.destroy()  # 关闭对话框
            else:
                # 验证失败
                status_var.set("无效的许可证密钥")
                verify_button.config(state=tk.NORMAL)
        except Exception as e:
            error_msg = f"验证出错: {str(e)}"
            status_var.set(error_msg)
            verify_button.config(state=tk.NORMAL)
    
    def on_cancel():
        """取消操作"""
        nonlocal result
        result['valid'] = False
        dialog_root.destroy()
    
    # 创建界面
    main_frame = ttk.Frame(dialog_root, padding=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # 提示标签
    ttk.Label(main_frame, text="请输入许可证密钥以继续使用软件：", font=("", 10)).pack(anchor=tk.W, pady=(0, 10))
    
    # 许可证密钥输入框
    frame = ttk.Frame(main_frame)
    frame.pack(fill=tk.X, pady=5)
    
    ttk.Label(frame, text="许可证密钥:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    
    license_key_entry = ttk.Entry(frame, textvariable=license_key_var, width=30, show="*")
    license_key_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
    
    ttk.Checkbutton(frame, text="显示", variable=show_key_var, 
                   command=toggle_key_visibility).grid(row=0, column=2, padx=5, pady=5)
    
    # 按钮区域
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=(20, 0))
    
    verify_button = ttk.Button(button_frame, text="验证", command=verify_license)
    verify_button.pack(side=tk.LEFT, padx=5)
    
    ttk.Button(button_frame, text="取消", command=on_cancel).pack(side=tk.RIGHT, padx=5)
    
    # 状态标签
    status_label = ttk.Label(main_frame, textvariable=status_var, foreground="red")
    status_label.pack(fill=tk.X, pady=(10, 0))
    
    # 绑定回车键
    license_key_entry.bind("<Return>", lambda e: verify_license())
    
    # 确保输入框获得焦点
    license_key_entry.focus_set()
    
    # 设置关闭按钮行为
    dialog_root.protocol("WM_DELETE_WINDOW", on_cancel)
    
    # 运行对话框
    dialog_root.mainloop()
    
    return result

class BatchRenameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("通义千问文件批量重命名工具")
        self.root.geometry("700x650")  # 调整高度以适应新增的许可证密钥输入框
        self.root.minsize(650, 550)
        
        # 检查截止日期
        self.check_expiration()
        
        # 创建变量
        self.folder_path_var = tk.StringVar()
        self.api_key_var = tk.StringVar()
        self.batch_size_var = tk.IntVar(value=3)
        self.show_key_var = tk.BooleanVar(value=False)
        self.remember_key_var = tk.BooleanVar(value=True)  # 记住API密钥变量
        self.model_var = tk.StringVar(value="qwen-plus")
        self.keyword_var = tk.StringVar() # 新增：关键字变量
        self.include_subdirs_var = tk.BooleanVar(value=True)  # 新增：包含子目录选项
        
        # 加载保存的API密钥
        self.load_api_key()
        
        # 创建界面
        self.create_widgets()
        
        # 初始化标志
        self.is_processing = False
    
    def load_api_key(self):
        """加载保存的API密钥"""
        try:
            key_file = Path('config/api_key.json')
            if key_file.exists():
                with open(key_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    saved_key = data.get('api_key', '')
                    if saved_key:
                        self.api_key_var.set(saved_key)
                        print("已加载保存的API密钥")
        except Exception as e:
            print(f"加载API密钥错误: {e}")
    
    def save_api_key(self):
        """保存API密钥"""
        if not self.remember_key_var.get():
            # 如果不记住密钥，尝试删除已保存的密钥
            try:
                key_file = Path('config/api_key.json')
                if key_file.exists():
                    os.remove(key_file)
                    print("已删除保存的API密钥")
            except Exception as e:
                print(f"删除API密钥文件错误: {e}")
            return
            
        try:
            api_key = self.api_key_var.get().strip()
            if not api_key:
                return
                
            # 确保配置目录存在
            os.makedirs('config', exist_ok=True)
            
            key_file = Path('config/api_key.json')
            with open(key_file, 'w', encoding='utf-8') as f:
                json.dump({'api_key': api_key}, f)
                
            print("API密钥已保存")
        except Exception as e:
            print(f"保存API密钥错误: {e}")
    
    def check_expiration(self):
        """检查软件是否过期"""
        today = datetime.datetime.now().date()
        expiration_date = datetime.date(2025, 5, 31)
        
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
        
        # 新增：包含子目录选项
        ttk.Checkbutton(input_frame, text="包含子目录", variable=self.include_subdirs_var).grid(row=0, column=3, padx=5, pady=5)
        
        # API密钥
        ttk.Label(input_frame, text="API密钥:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.api_key_entry = ttk.Entry(input_frame, textvariable=self.api_key_var, width=50, show="*")
        self.api_key_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # API密钥操作按钮区
        api_key_buttons = ttk.Frame(input_frame)
        api_key_buttons.grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        
        ttk.Checkbutton(api_key_buttons, text="显示", variable=self.show_key_var, 
                       command=self.toggle_key_visibility).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Checkbutton(api_key_buttons, text="记住密钥", variable=self.remember_key_var).pack(side=tk.LEFT)

        # 新增：关键字输入
        ttk.Label(input_frame, text="关键字:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(input_frame, textvariable=self.keyword_var, width=50).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)

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
        
        # 保存API密钥（如果用户选择记住）
        self.save_api_key()
        
        # 获取关键字
        keyword = self.keyword_var.get().strip() # 新增：获取关键字
        include_subdirs = self.include_subdirs_var.get()  # 获取是否包含子目录的选项

        # 更新UI状态
        self.is_processing = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("正在处理...")
        self.progress.start()
        
        # 在新线程中执行处理，避免界面卡死
        thread = threading.Thread(target=self.process_files, args=(folder_path, api_key, keyword, include_subdirs)) # 修改：传递include_subdirs参数
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
    
    def process_files(self, folder_path, api_key, keyword, include_subdirs=False): # 修改：接收include_subdirs参数
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
            
            # 获取文件列表（支持递归扫描子目录）
            file_info_list = []
            
            if include_subdirs:
                self.log("正在递归扫描所有子目录中的文件...")
                for root, _, files in os.walk(folder_path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        rel_dir = os.path.relpath(root, folder_path)
                        # 如果是根目录，rel_dir为"."，我们将其置为空字符串
                        if rel_dir == ".":
                            rel_dir = ""
                        file_info_list.append((full_path, file, rel_dir))
            else:
                self.log("仅扫描当前目录中的文件...")
                for file in os.listdir(folder_path):
                    full_path = os.path.join(folder_path, file)
                    if os.path.isfile(full_path):
                        file_info_list.append((full_path, file, ""))
            
            self.log(f"找到{len(file_info_list)}个文件")
            
            # 设置进度条最大值
            total_batches = (len(file_info_list) - 1) // batch_size + 1
            self.root.after(0, lambda: self.progress.config(mode='determinate', maximum=total_batches))
            self.progress_var.set(0)
            
            # 批量处理文件
            for i in range(0, len(file_info_list), batch_size):
                if not self.is_processing:
                    break
                    
                batch_file_info = file_info_list[i:i+batch_size]
                batch_num = i // batch_size + 1
                
                # 提取当前批次的文件名（用于显示）
                batch_files = [info[1] for info in batch_file_info]
                
                self.log(f"\n处理批次 {batch_num}/{total_batches}，共{len(batch_files)}个文件:")
                
                # 更新进度条
                self.root.after(0, lambda v=batch_num: self.progress_var.set(v))
                
                # 构建提示
                file_list_text = "\n".join([f"{idx+1}. {file}" for idx, file in enumerate(batch_files)])
                
                # 修改：根据是否有关键字调整提示逻辑
                if keyword:
                    primary_instruction = f"请根据关键字 '{keyword}' 来为以下文件命名。"
                    secondary_instruction = "生成的新文件名应关于此关键字，并保持简洁、吸引人。可以很大程度上忽略原始文件名（除了扩展名）。"
                else:
                    primary_instruction = "请帮我优化以下文件名，生成更加简洁、清晰的新文件名。"
                    secondary_instruction = "每个文件名需要花哨一些，不要过于简单。"

                prompt = f"""{primary_instruction}
{secondary_instruction}
保留原文件名的扩展名(.jpg/.mp4等)。
请严格按照以下格式返回结果，只需返回编号和新文件名，不要包含其他任何说明文字或注释：

原文件列表:
{file_list_text}

新文件名:
1. [新文件名1]
2. [新文件名2]
... (根据文件数量继续)
"""
                
                try:
                    # 调用通义千问API
                    self.log("正在请求通义千问API...")
                    self.log(f"发送的Prompt:\n{prompt}") # 添加日志输出Prompt内容
                    response = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": "你是一个专业的文件重命名助手，擅长根据用户需求生成文件名。"},
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
                        line = line.strip() # 去除前后空格
                        if line and line[0].isdigit() and '. ' in line:
                            parts = line.split('. ', 1)
                            if len(parts) == 2 and parts[0].isdigit():
                                try: # 添加try-except以防非数字
                                    idx = int(parts[0]) - 1
                                    if 0 <= idx < len(batch_files):
                                        new_name = parts[1].strip().strip('[]')
                                        # 进一步清理可能的markdown标记
                                        new_name = new_name.replace('*', '').replace('`', '') 
                                        if new_name:
                                            new_filenames.append((idx, new_name))
                                except ValueError:
                                    self.log(f"警告：无法解析行号: {line}")
                                    continue
                    
                    # 直接执行重命名操作，不显示确认对话框
                    if new_filenames and self.is_processing:
                        self.log("\n开始执行重命名操作:")
                        renamed_count = 0 # 记录成功重命名的数量
                        for idx, new_name in new_filenames:
                            if not self.is_processing:
                                break
                            
                            # 获取完整信息
                            old_path, old_name, rel_dir = batch_file_info[idx]
                            
                            # 保留原扩展名
                            name_part, ext = os.path.splitext(old_name)
                            # 确保新文件名不为空且不包含非法字符 (简单检查)
                            new_name = "".join(c for c in new_name if c not in '/\\:*?"<>|') 
                            if not new_name:
                                self.log(f"警告：生成的新文件名无效或为空，跳过: {old_name}")
                                continue

                            # 检查新文件名是否与旧扩展名匹配，如果不匹配则添加
                            new_name_part, new_ext = os.path.splitext(new_name)
                            if not new_ext: # 如果AI生成的不带扩展名
                                final_new_name = new_name_part + ext
                            elif new_ext.lower() != ext.lower(): # 如果AI生成的扩展名不对
                                self.log(f"警告：AI生成的扩展名 '{new_ext}' 与原扩展名 '{ext}' 不符，将使用原扩展名。")
                                final_new_name = new_name_part + ext
                            else: # AI生成的扩展名正确
                                final_new_name = new_name

                            # 避免重命名为同名文件
                            if final_new_name == old_name:
                                self.log(f"跳过重命名，新旧文件名相同: {old_name}")
                                continue

                            # 确定目标文件路径
                            parent_dir = os.path.dirname(old_path)
                            new_path = os.path.join(parent_dir, final_new_name)
                            
                            # 处理潜在的文件名冲突
                            counter = 1
                            base_name, file_ext = os.path.splitext(final_new_name)
                            while os.path.exists(new_path):
                                self.log(f"警告：目标文件 '{final_new_name}' 已存在。尝试添加后缀...")
                                final_new_name = f"{base_name}_{counter}{file_ext}"
                                new_path = os.path.join(parent_dir, final_new_name)
                                counter += 1
                                if counter > 10: # 防止无限循环
                                    self.log(f"错误：无法为 '{old_name}' 找到不冲突的新文件名，跳过。")
                                    final_new_name = None
                                    break
                            
                            if final_new_name is None:
                                continue # 跳到下一个文件

                            # 显示包含相对路径的日志
                            path_info = f"[{rel_dir}]" if rel_dir else ""
                            self.log(f"准备重命名: {path_info}{old_name} -> {final_new_name}")
                            
                            try:
                                os.rename(old_path, new_path)
                                self.log(f"已重命名: {path_info}{old_name} -> {final_new_name}")
                                renamed_count += 1
                            except OSError as e: # 更具体的异常捕获
                                self.log(f"重命名失败: {path_info}{old_name} -> {final_new_name} - 错误: {e}")
                            except Exception as e:
                                self.log(f"重命名时发生未知错误: {path_info}{old_name} - {e}")
                                self.log(traceback.format_exc()) # 记录完整堆栈

                        if renamed_count > 0:
                             self.log(f"本批次成功重命名 {renamed_count} 个文件。")
                        else:
                             self.log("本批次未能成功重命名任何文件。")
                             
                    elif not new_filenames and self.is_processing:
                        self.log("无法从API响应中提取有效的文件名或格式不符")
                    elif not self.is_processing:
                        self.log("处理已停止，未执行重命名。")
                        
                except Exception as e:
                    self.log(f"处理批次 {batch_num} 时出错: {str(e)}")
                    self.log(traceback.format_exc())  # 添加错误堆栈以便调试
                    # 考虑是否继续处理下一批
                
                # 避免API限流，添加延迟
                if i + batch_size < len(file_info_list) and self.is_processing:
                    delay = 2  # 2秒延迟
                    self.log(f"\n等待{delay}秒，避免API限流...")
                    time.sleep(delay)
            
            # 完成处理
            if self.is_processing:
                self.log("\n所有文件处理完成!")
                self.status_var.set("处理完成")
            
        except Exception as e:
            self.log(f"发生严重错误: {str(e)}")
            self.log(traceback.format_exc())
            self.status_var.set("处理过程中发生严重错误")
        
        # 恢复UI状态
        self.is_processing = False
        self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.stop_button.config(state=tk.DISABLED))
        self.root.after(0, lambda: self.progress.stop())

    def log(self, message):
        """添加消息到日志区域"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)  # 滚动到底部
        self.root.update_idletasks()

def main():
    """主函数"""
    # 创建日志目录
    os.makedirs('logs', exist_ok=True)
    
    # 创建配置目录
    os.makedirs('config', exist_ok=True)
    
    try:
        # 直接启动主程序
        root = tk.Tk()
        app = BatchRenameGUI(root)
        root.mainloop()
            
    except Exception as e:
        print(f"程序启动异常: {e}")
        traceback.print_exc()
        
        # 尝试显示错误对话框
        try:
            messagebox.showerror("启动错误", f"程序启动失败: {e}\n请联系开发者")
        except:
            pass

if __name__ == "__main__":
    main() 