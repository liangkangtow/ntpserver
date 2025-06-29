#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NTP校时服务端
支持从多个NTP服务器获取最新时间，并为客户端提供校时服务
"""

import socket
import struct
import time
import threading
import logging
from datetime import datetime, timezone
import ntplib
from typing import List, Dict, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ntp_server.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NTPServer:
    """NTP校时服务器"""
    
    def __init__(self, host='0.0.0.0', port=123, sync_interval=300):
        """
        初始化NTP服务器
        
        Args:
            host: 监听地址
            port: 监听端口
            sync_interval: 时间同步间隔（秒）
        """
        self.host = host
        self.port = port
        self.sync_interval = sync_interval
        self.running = False
        self.server_socket = None
        
        # NTP服务器列表（用于时间同步）
        self.ntp_servers = [
            'ntp.aliyun.com',
            'cn.pool.ntp.org',
            'ntp1.aliyun.com',
            'ntp2.aliyun.com'
        ]
        
        # 当前时间偏移量
        self.time_offset = 0.0
        self.last_sync_time = 0
        self.sync_lock = threading.Lock()
        
        # 客户端连接统计
        self.client_stats = {
            'total_connections': 0,
            'active_connections': 0,
            'last_client_time': None
        }
        self.stats_lock = threading.Lock()
        
        # 创建NTP客户端
        self.ntp_client = ntplib.NTPClient()
    
    def sync_time(self) -> bool:
        """
        从多个NTP服务器同步时间
        
        Returns:
            bool: 同步是否成功
        """
        try:
            logger.info("开始时间同步...")
            
            responses = []
            for server in self.ntp_servers:
                try:
                    response = self.ntp_client.request(server, version=3, timeout=10)
                    if response:
                        responses.append(response)
                        logger.debug(f"从 {server} 获取时间: {response.tx_time}")
                except Exception as e:
                    logger.warning(f"从 {server} 同步时间失败: {e}")
            
            if not responses:
                logger.error("所有NTP服务器都无法连接")
                return False
            
            # 计算平均偏移量
            offsets = []
            for response in responses:
                offset = response.offset
                if abs(offset) < 1000.0:  # 临时放宽过滤条件，允许最大1000秒
                    offsets.append(offset)
            
            if not offsets:
                logger.warning("所有时间偏移量都被过滤")
                return False
            
            # 使用中位数作为最终偏移量
            offsets.sort()
            median_offset = offsets[len(offsets) // 2]
            
            with self.sync_lock:
                self.time_offset = median_offset
                self.last_sync_time = time.time()
            
            logger.info(f"时间同步完成，偏移量: {median_offset:.6f}秒")
            return True
            
        except Exception as e:
            logger.error(f"时间同步失败: {e}")
            return False
    
    def get_current_time(self) -> float:
        """
        获取当前准确时间（考虑偏移量）
        
        Returns:
            float: 当前时间戳
        """
        with self.sync_lock:
            return time.time() + self.time_offset
    
    def create_ntp_packet(self, mode=3) -> bytes:
        """
        创建NTP数据包
        
        Args:
            mode: NTP模式（3=客户端，4=服务器）
        
        Returns:
            bytes: NTP数据包
        """
        # NTP v3 数据包格式
        packet = bytearray(48)
        
        # 版本号(3)和模式
        packet[0] = (3 << 3) | mode
        
        # 轮询间隔
        packet[2] = 4  # 16秒
        
        # 精度
        packet[3] = 0xFA  # 2^-6 = 15.625ms
        
        # 根延迟
        struct.pack_into('!I', packet, 4, 0x00010000)  # 1秒
        
        # 根分散
        struct.pack_into('!I', packet, 8, 0x00010000)  # 1秒
        
        # 参考标识符
        struct.pack_into('!I', packet, 12, 0x4E545031)  # "NTP1"
        
        # 参考时间戳
        ref_time = self.get_current_time()
        struct.pack_into('!Q', packet, 16, int(ref_time * 2**32))
        
        # 原始时间戳
        struct.pack_into('!Q', packet, 24, int(ref_time * 2**32))
        
        # 接收时间戳
        recv_time = self.get_current_time()
        struct.pack_into('!Q', packet, 32, int(recv_time * 2**32))
        
        # 传输时间戳
        xmit_time = self.get_current_time()
        struct.pack_into('!Q', packet, 40, int(xmit_time * 2**32))
        
        return bytes(packet)
    
    def parse_ntp_packet(self, data: bytes) -> Dict:
        """
        解析NTP数据包
        
        Args:
            data: NTP数据包
        
        Returns:
            Dict: 解析结果
        """
        if len(data) < 48:
            return None
        
        # 解析头部
        li_vn_mode = data[0]
        version = (li_vn_mode >> 3) & 0x07
        mode = li_vn_mode & 0x07
        
        # 解析时间戳
        transmit_time = struct.unpack('!Q', data[40:48])[0] / 2**32
        
        return {
            'version': version,
            'mode': mode,
            'transmit_time': transmit_time
        }
    
    def handle_client(self, client_socket: socket.socket, client_address: tuple):
        """
        处理客户端连接
        
        Args:
            client_socket: 客户端套接字
            client_address: 客户端地址
        """
        try:
            with self.stats_lock:
                self.client_stats['total_connections'] += 1
                self.client_stats['active_connections'] += 1
                self.client_stats['last_client_time'] = datetime.now()
            
            logger.info(f"客户端连接: {client_address}")
            
            while self.running:
                try:
                    # 接收客户端数据
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    
                    # 解析NTP请求
                    request = self.parse_ntp_packet(data)
                    if not request:
                        logger.warning(f"无效的NTP数据包来自 {client_address}")
                        continue
                    
                    # 创建响应数据包
                    response = self.create_ntp_packet(mode=4)
                    
                    # 发送响应
                    client_socket.send(response)
                    
                    logger.debug(f"为客户端 {client_address} 提供校时服务")
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    logger.error(f"处理客户端 {client_address} 时出错: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"客户端 {client_address} 连接错误: {e}")
        finally:
            client_socket.close()
            with self.stats_lock:
                self.client_stats['active_connections'] -= 1
            logger.info(f"客户端断开连接: {client_address}")
    
    def start(self):
        """启动NTP服务器"""
        try:
            # 创建服务器套接字
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.server_socket.settimeout(1.0)
            
            self.running = True
            logger.info(f"NTP服务器启动，监听 {self.host}:{self.port}")
            
            # 启动时间同步线程
            sync_thread = threading.Thread(target=self._sync_worker, daemon=True)
            sync_thread.start()
            
            # 主循环处理客户端连接
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    client_thread.start()
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        logger.error(f"接受客户端连接时出错: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"启动NTP服务器失败: {e}")
        finally:
            self.stop()
    
    def _sync_worker(self):
        """时间同步工作线程"""
        while self.running:
            try:
                self.sync_time()
                time.sleep(self.sync_interval)
            except Exception as e:
                logger.error(f"时间同步线程错误: {e}")
                time.sleep(60)  # 出错时等待1分钟后重试
    
    def stop(self):
        """停止NTP服务器"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        logger.info("NTP服务器已停止")
    
    def get_status(self) -> Dict:
        """
        获取服务器状态
        
        Returns:
            Dict: 服务器状态信息
        """
        with self.sync_lock:

            return {
                'running': self.running,
                'host': self.host,
                'port': self.port,
                'time_offset': self.time_offset,
                'last_sync_time': self.last_sync_time,
                'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'client_stats': self.client_stats.copy()
            }

if __name__ == '__main__':
    # 创建并启动NTP服务器
    server = NTPServer()
    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在停止服务器...")
        server.stop() 