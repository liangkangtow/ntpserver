#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NTP服务器快速测试脚本
验证基本功能是否正常
"""

import time
import threading
import subprocess
import sys
from ntp_server import NTPServer
from ntp_client_test import test_ntp_server

def test_time_sync():
    """测试时间同步功能"""
    print("测试时间同步功能...")
    
    server = NTPServer(host='127.0.0.1', port=12345, sync_interval=60)
    
    # 测试时间同步
    success = server.sync_time()
    if success:
        print("✓ 时间同步功能正常")
        print(f"  时间偏移: {server.time_offset:.6f} 秒")
        print(f"  当前时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(server.get_current_time()))}")
    else:
        print("✗ 时间同步功能异常")
    
    return success

def test_ntp_packet():
    """测试NTP数据包创建和解析"""
    print("\n测试NTP数据包功能...")
    
    server = NTPServer()
    
    try:
        # 测试创建数据包
        packet = server.create_ntp_packet(mode=4)
        if len(packet) == 48:
            print("✓ NTP数据包创建正常")
        else:
            print("✗ NTP数据包创建异常")
            return False
        
        # 测试解析数据包
        parsed = server.parse_ntp_packet(packet)
        if parsed and 'version' in parsed:
            print("✓ NTP数据包解析正常")
        else:
            print("✗ NTP数据包解析异常")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ NTP数据包测试失败: {e}")
        return False

def test_server_startup():
    """测试服务器启动功能"""
    print("\n测试服务器启动功能...")
    
    server = NTPServer(host='127.0.0.1', port=12346, sync_interval=60)
    
    try:
        # 启动服务器线程
        server_thread = threading.Thread(target=server.start, daemon=True)
        server_thread.start()
        
        # 等待服务器启动
        time.sleep(3)
        
        if server.running:
            print("✓ 服务器启动正常")
            
            # 测试客户端连接
            time.sleep(1)
            success = test_ntp_server('127.0.0.1', 12346, 3)
            
            # 停止服务器
            server.stop()
            time.sleep(1)
            
            return success
        else:
            print("✗ 服务器启动失败")
            return False
            
    except Exception as e:
        print(f"✗ 服务器启动测试失败: {e}")
        return False

def main():
    print("🕐 NTP服务器快速功能测试")
    print("=" * 40)
    
    # 检查依赖
    try:
        import ntplib
        import flask
        print("✓ 依赖检查通过")
    except ImportError as e:
        print(f"✗ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return
    
    # 运行测试
    tests = [
        ("时间同步", test_time_sync),
        ("NTP数据包", test_ntp_packet),
        ("服务器启动", test_server_startup)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name}测试异常: {e}")
            results.append((test_name, False))
    
    # 显示测试结果
    print("\n" + "=" * 40)
    print("测试结果汇总:")
    print("=" * 40)
    
    passed = 0
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(results)} 项测试通过")
    
    if passed == len(results):
        print("🎉 所有测试通过！NTP服务器功能正常")
    else:
        print("⚠️  部分测试失败，请检查配置和网络连接")

if __name__ == '__main__':
    main() 