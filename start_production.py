#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NTP服务器生产环境启动脚本
使用WSGI服务器运行Web界面
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import ntplib
        import flask
        import requests
        print("✓ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"✗ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def install_wsgi_server():
    """安装WSGI服务器"""
    try:
        import waitress
        print("✓ WSGI服务器已安装")
        return True
    except ImportError:
        print("安装WSGI服务器 (waitress)...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'waitress'])
            print("✓ WSGI服务器安装成功")
            return True
        except subprocess.CalledProcessError:
            print("✗ WSGI服务器安装失败")
            return False

def start_with_waitress():
    """使用waitress启动Web服务"""
    try:
        from waitress import serve
        from web_interface import app
        
        print("使用生产级WSGI服务器启动...")
        print("访问地址: http://localhost:5000")
        print("按 Ctrl+C 停止服务")
        
        # 启动WSGI服务器
        serve(app, host='0.0.0.0', port=5000, threads=4)
        
    except ImportError:
        print("✗ waitress未安装，回退到开发服务器")
        start_with_flask()
    except Exception as e:
        print(f"✗ 启动失败: {e}")
        start_with_flask()

def start_with_flask():
    """使用Flask开发服务器启动"""
    print("使用Flask开发服务器启动...")
    print("访问地址: http://localhost:5000")
    print("按 Ctrl+C 停止服务")
    
    # 清除可能的环境变量
    env = os.environ.copy()
    if 'WERKZEUG_RUN_MAIN' in env:
        del env['WERKZEUG_RUN_MAIN']
    if 'WERKZEUG_SERVER_FD' in env:
        del env['WERKZEUG_SERVER_FD']
    
    try:
        subprocess.run([sys.executable, 'web_interface.py'], env=env)
    except KeyboardInterrupt:
        print("\n服务已停止")

def main():
    print("🕐 NTP校时服务器 - 生产环境启动器")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 安装WSGI服务器
    if not install_wsgi_server():
        print("将使用Flask开发服务器")
    
    print("\n选择启动模式:")
    print("1. 生产环境 (WSGI服务器)")
    print("2. 开发环境 (Flask服务器)")
    print("3. 直接运行NTP服务器")
    print("4. 测试NTP服务器")
    print("5. 退出")
    
    while True:
        try:
            choice = input("\n请输入选择 (1-5): ").strip()
            
            if choice == '1':
                print("\n启动生产环境Web管理界面...")
                start_with_waitress()
                break
                
            elif choice == '2':
                print("\n启动开发环境Web管理界面...")
                start_with_flask()
                break
                
            elif choice == '3':
                print("\n直接启动NTP服务器...")
                print("按 Ctrl+C 停止服务")
                try:
                    subprocess.run([sys.executable, 'ntp_server.py'])
                except KeyboardInterrupt:
                    print("\n服务已停止")
                break
                
            elif choice == '4':
                print("\n启动NTP服务器测试...")
                subprocess.run([sys.executable, 'ntp_client_test.py'])
                break
                
            elif choice == '5':
                print("退出")
                break
                
            else:
                print("无效选择，请输入1-5")
                
        except KeyboardInterrupt:
            print("\n退出")
            break
        except Exception as e:
            print(f"错误: {e}")
            break

if __name__ == '__main__':
    main() 