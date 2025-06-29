#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NTP客户端测试工具
用于测试NTP服务器的校时功能
"""

import socket
import struct
import time
import ntplib
from datetime import datetime
import argparse

def create_ntp_request() -> bytes:
    """创建NTP请求数据包"""
    packet = bytearray(48)
    
    # 版本号(3)和模式(3=客户端)
    packet[0] = (3 << 3) | 3
    
    # 轮询间隔
    packet[2] = 4  # 16秒
    
    # 精度
    packet[3] = 0xFA  # 2^-6 = 15.625ms
    
    # 传输时间戳
    xmit_time = time.time()
    struct.pack_into('!Q', packet, 40, int(xmit_time * 2**32))
    
    return bytes(packet)

def parse_ntp_response(data: bytes) -> dict:
    """解析NTP响应数据包"""
    if len(data) < 48:
        return None
    
    # 解析时间戳
    ref_time = struct.unpack('!Q', data[16:24])[0] / 2**32
    orig_time = struct.unpack('!Q', data[24:32])[0] / 2**32
    recv_time = struct.unpack('!Q', data[32:40])[0] / 2**32
    xmit_time = struct.unpack('!Q', data[40:48])[0] / 2**32
    
    return {
        'ref_time': ref_time,
        'orig_time': orig_time,
        'recv_time': recv_time,
        'xmit_time': xmit_time
    }

def test_ntp_server(host: str, port: int = 123, timeout: int = 5):
    """测试NTP服务器"""
    print(f"正在测试NTP服务器 {host}:{port}...")
    
    try:
        # 创建套接字
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        # 连接服务器
        sock.connect((host, port))
        print(f"✓ 成功连接到 {host}:{port}")
        
        # 发送NTP请求
        request = create_ntp_request()
        sock.send(request)
        print("✓ 已发送NTP请求")
        
        # 接收响应
        response = sock.recv(1024)
        sock.close()
        
        if not response:
            print("✗ 未收到响应")
            return False
        
        # 解析响应
        ntp_data = parse_ntp_response(response)
        if not ntp_data:
            print("✗ 响应数据格式错误")
            return False
        
        # 计算时间偏移
        t1 = time.time()  # 发送时间
        t2 = ntp_data['recv_time']  # 服务器接收时间
        t3 = ntp_data['xmit_time']  # 服务器发送时间
        t4 = time.time()  # 接收时间
        
        delay = (t4 - t1) - (t3 - t2)
        offset = ((t2 - t1) + (t3 - t4)) / 2
        
        print("✓ 收到有效NTP响应")
        print(f"  服务器时间: {datetime.fromtimestamp(t3)}")
        print(f"  本地时间: {datetime.fromtimestamp(t1)}")
        print(f"  网络延迟: {delay:.6f} 秒")
        print(f"  时间偏移: {offset:.6f} 秒")
        
        return True
        
    except socket.timeout:
        print(f"✗ 连接超时 ({timeout}秒)")
        return False
    except ConnectionRefusedError:
        print(f"✗ 连接被拒绝 - 服务器可能未运行")
        return False
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def test_public_ntp_servers():
    """测试公共NTP服务器作为对比"""
    print("\n" + "="*50)
    print("测试公共NTP服务器作为对比")
    print("="*50)
    
    public_servers = [
        'time.windows.com',
        'time.nist.gov',
        'pool.ntp.org'
    ]
    
    for server in public_servers:
        print(f"\n测试 {server}:")
        test_ntp_server(server)

def main():
    parser = argparse.ArgumentParser(description='NTP客户端测试工具')
    parser.add_argument('host', nargs='?', default='localhost', 
                       help='NTP服务器地址 (默认: localhost)')
    parser.add_argument('-p', '--port', type=int, default=123,
                       help='NTP服务器端口 (默认: 123)')
    parser.add_argument('-t', '--timeout', type=int, default=5,
                       help='连接超时时间 (默认: 5秒)')
    parser.add_argument('--compare', action='store_true',
                       help='同时测试公共NTP服务器进行对比')
    
    args = parser.parse_args()
    
    print("NTP客户端测试工具")
    print("="*50)
    
    # 测试指定的NTP服务器
    success = test_ntp_server(args.host, args.port, args.timeout)
    
    if args.compare:
        test_public_ntp_servers()
    
    if success:
        print(f"\n✓ NTP服务器 {args.host}:{args.port} 工作正常")
    else:
        print(f"\n✗ NTP服务器 {args.host}:{args.port} 测试失败")

if __name__ == '__main__':
    main() 