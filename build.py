#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
通义千问文件批量重命名工具打包脚本
使用PyInstaller将GUI应用打包成可执行文件
"""

import os
import sys
import shutil
import subprocess
import datetime
import argparse

def check_pyinstaller():
    """检查是否安装了PyInstaller，如果没有则安装"""
    try:
        import PyInstaller
        print("✓ PyInstaller已安装")
    except ImportError:
        print("PyInstaller未安装，正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller安装成功")

def check_dependencies():
    """检查并安装所需依赖"""
    dependencies = ["openai", "httpx", "requests"]
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✓ {dep}已安装")
        except ImportError:
            print(f"{dep}未安装，正在安装...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"✓ {dep}安装成功")

def create_icon():
    """创建临时图标文件，如果没有找到图标文件"""
    icon_path = "icon.ico"
    if os.path.exists(icon_path):
        return icon_path
    
    try:
        import base64
        # 这是一个简单的文件图标的base64编码
        icon_data = """
        AAABAAEAICAAAAEAIACoEAAAFgAAACgAAAAgAAAAQAAAAAEAIAAAAAAAABAAAMMOAADDDgAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACqgGYA////AP///wD///8A
        ////AP///wCqgGYAqoBmAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKqAZgCqgGYAqoBm
        AP///wCqgGYAqoBmAKqAZgCqgGYAqoBmAKqAZgCqgGYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACqgGYAqoBm
        AKqAZgCqgGYAqoBmAP///wCqgGYAqoBmAKqAZgCqgGYAqoBmAKqAZgCqgGYAqoBmAKqAZgAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAqoBm
        AKqAZgCqgGYAqoBmAKqAZgCqgGYA////AKqAZgD///8AqoBmAKqAZgCqgGYAqoBmAKqAZgCqgGYA
        qoBmAKqAZgCqgGYAqoBmAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAqoBmAKqAZgCqgGYAqoBmAKqAZgCqgGYAqoBmAP///wCqgGYA////AKqAZgCqgGYAqoBmAKqA
        ZgCqgGYAqoBmAKqAZgCqgGYAqoBmAKqAZgCqgGYAqoBmAKqAZgCqgGYAqoBmAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAKqAZgCqgGYAqoBmAKqAZgCqgGYAqoBmAKqAZgCqgGYA////AKqAZgD///8AqoBm
        AKqAZgCqgGYAqoBmAKqAZgCqgGYAqoBmAKqAZgCqgGYAqoBmAKqAZgCqgGYAqoBmAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAqoBmAKqAZgCqgGYAqoBmAKqAZgCqgGYAqoBmAKqAZgD///8AqoBm
        AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wCqgGYAqoBmAKqAZgCqgGYA
        qoBmAKqAZgAAAAAAAAAAAAAAAAAAAAAAqoBmAKqAZgCqgGYAqoBmAKqAZgCqgGYAqoBmAKqAZgCq
        gGYA////AKqAZgD///8AqoBmAKqAZgCqgGYAqoBmAKqAZgCqgGYAqoBmAKqAZgD///8AqoBmAKqA
        ZgCqgGYAqoBmAKqAZgCqgGYAqoBmAAAAAAAAAAAAqoBmAKqAZgCqgGYAqoBmAKqAZgCqgGYAqoBm
        AKqAZgCqgGYA////AKqAZgD///8AqoBmAKqAZgCqgGYAqoBmAKqAZgCqgGYAqoBmAKqAZgD///8A
        qoBmAKqAZgCqgGYAqoBmAKqAZgCqgGYAqoBmAKqAZgAAAAAAAAAAAKqAZgCqgGYAqoBmAKqAZgCq
        gGYAqoBmAKqAZgCqgGYAqoBmAKqAZgCqgGYAqoBmAKqAZgD///8AqoBmAKqAZgCqgGYAqoBmAKqAZg
        CqgGYAqoBmAKqAZgCqgGYAqoBmAAAAAAAAAAAAAAAAAAAAAAAAAAAAqoBm
        AKqAZgCqgGYAqoBmAKqAZgCqgGYAqoBmAKqAZgCqgGYAqoBmAKqAZgCqgGYAqoBmAKqAZgD///8A
        qoBmAKqAZgCqgGYAqoBmAKqAZgCqgGYAqoBmAKqAZgCqgGYAqoBmAKqAZgCqgGYAqoBmAKqAZgCqg
        GYAqoBmAKqAZgCqgGYAqoBmAAAAAAAAAAAAAAAAAAAAAAAAAAAAqoBm
        AKqAZgCqgGYAqoBmAKqAZgD///8AqoBmAP///wD///8A////AP///wD///8A////AP///wD///8A
        ////AP///wCqgGYAqoBmAKqAZgCqgGYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAqoBmAKqAZgCqgGYAqoBmAP///wCqgGYAqoBmAKqAZgCqgGYAqoBm
        AKqAZgCqgGYAqoBmAKqAZgCqgGYAqoBmAKqAZgCqgGYAqoBmAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACqgGYAqoBmAKqAZgCqgGYAqoBmAKqAZgCqgGYA
        qoBmAKqAZgCqgGYAqoBmAKqAZgCqgGYAqoBmAKqAZgAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACqgGYAqoBmAKqAZgD///8AqoBm
        AKqAZgCqgGYAqoBmAKqAZgCqgGYAqoBmAKqAZgCqgGYAqoBmAKqAZgAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAqoBm
        AP///wD///8A////AP///wD///8A////AP///wCqgGYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=
        """
        icon_data = base64.b64decode(icon_data.strip())
        with open(icon_path, "wb") as f:
            f.write(icon_data)
        print(f"✓ 创建了临时图标文件: {icon_path}")
        return icon_path
    except:
        print("⚠ 无法创建图标文件，将使用默认图标")
        return None

def build_app(one_file=True, debug=False, icon=None):
    """使用PyInstaller打包应用"""
    print("\n开始打包应用...")
    
    # 确定文件名
    current_date = datetime.datetime.now().strftime("%Y%m%d")
    output_name = f"通义千问文件批量重命名工具_v{current_date}"
    
    # 构建命令
    cmd = [
        "pyinstaller",
        "--name", output_name,
        "--noconfirm",  # 覆盖现有输出
        "--clean",  # 在构建前清理
    ]
    
    # 添加图标
    if icon:
        cmd.extend(["--icon", icon])
    
    # 单文件模式
    if one_file:
        cmd.append("--onefile")
    
    # 无控制台窗口
    if not debug:
        cmd.append("--windowed")
    
    # 添加需要隐式包含的模块
    cmd.extend([
        "--hidden-import", "datetime",
        "--hidden-import", "httpx",
        "--hidden-import", "openai",
    ])
    
    # 设置入口文件
    cmd.append("gui.py")
    
    # 执行命令
    print(f"执行命令: {' '.join(cmd)}")
    subprocess.call(cmd)
    
    # 构建完成后的操作
    dist_dir = os.path.join("dist")
    if os.path.exists(dist_dir):
        print(f"\n✓ 打包完成! 可执行文件位于: {dist_dir}")
        if one_file:
            exe_path = os.path.join(dist_dir, f"{output_name}.exe")
            if os.path.exists(exe_path):
                print(f"✓ 可执行文件: {exe_path}")
                # 将可执行文件复制到当前目录
                target_path = f"{output_name}.exe"
                shutil.copy2(exe_path, target_path)
                print(f"✓ 已将可执行文件复制到当前目录: {target_path}")
    else:
        print("⚠ 构建失败，未找到输出目录")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="打包通义千问文件批量重命名工具")
    parser.add_argument('--dir', action='store_true', help='生成目录而非单个文件')
    parser.add_argument('--debug', action='store_true', help='显示控制台窗口')
    parser.add_argument('--no-icon', action='store_true', help='不使用图标')
    args = parser.parse_args()
    
    print("=" * 60)
    print("通义千问文件批量重命名工具打包脚本")
    print("=" * 60)
    
    # 检查依赖
    check_pyinstaller()
    check_dependencies()
    
    # 创建图标
    icon = None if args.no_icon else create_icon()
    
    # 构建应用
    build_app(one_file=not args.dir, debug=args.debug, icon=icon)
    
    print("\n构建过程完成!")
    print("注意: 构建的应用将在2024年3月31日后自动停止工作")
    print("=" * 60)

if __name__ == "__main__":
    main() 