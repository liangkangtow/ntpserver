#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NTP服务器启动脚本
提供简单的启动方式
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

def check_port_available(port):
    """检查端口是否可用"""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

def main():
    print("🕐 NTP校时服务器启动器")
    print("=" * 40)
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 检查端口
    if not check_port_available(5000):
        print("✗ 端口5000已被占用，请关闭其他Web服务")
        return
    
    print("\n选择启动模式:")
    print("1. Web管理界面 (推荐)")
    print("2. 直接运行NTP服务器")
    print("3. 测试NTP服务器")
    print("4. 退出")
    
    while True:
        try:
            choice = input("\n请输入选择 (1-4): ").strip()
            
            if choice == '1':
                print("\n启动Web管理界面...")
                print("访问地址: http://localhost:5000")
                print("按 Ctrl+C 停止服务")
                try:
                    subprocess.run([sys.executable, 'web_interface.py'])
                except KeyboardInterrupt:
                    print("\n服务已停止")
                break
                
            elif choice == '2':
                print("\n直接启动NTP服务器...")
                print("按 Ctrl+C 停止服务")
                try:
                    subprocess.run([sys.executable, 'ntp_server.py'])
                except KeyboardInterrupt:
                    print("\n服务已停止")
                break
                
            elif choice == '3':
                print("\n启动NTP服务器测试...")
                subprocess.run([sys.executable, 'ntp_client_test.py'])
                break
                
            elif choice == '4':
                print("退出")
                break
                
            else:
                print("无效选择，请输入1-4")
                
        except KeyboardInterrupt:
            print("\n退出")
            break
        except Exception as e:
            print(f"错误: {e}")
            break

if __name__ == '__main__':
    main() 