#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NTP服务器Web管理界面
提供服务器状态监控和管理功能
"""

from flask import Flask, render_template, jsonify, request
import threading
import time
import os
from datetime import datetime
from ntp_server import NTPServer
import sys

app = Flask(__name__)

# 全局NTP服务器实例
ntp_server = None
server_thread = None

def start_ntp_server():
    """在后台线程中启动NTP服务器"""
    global ntp_server
    ntp_server = NTPServer(host='0.0.0.0', port=123, sync_interval=300)
    ntp_server.start()

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    if ntp_server is None:
        return jsonify({
            'error': 'NTP服务器未启动',
            'running': False,
            'host': None,
            'port': None,
            'time_offset': None,
            'last_sync_time': None,
            'current_time': None,
            'client_stats': {
                'total_connections': 0,
                'active_connections': 0,
                'last_client_time': None
            }
        })
    status = ntp_server.get_status()
    
    # 格式化时间信息
    if status['last_sync_time'] > 0:
        last_sync = datetime.fromtimestamp(status['last_sync_time']).strftime('%Y-%m-%d %H:%M:%S')
    else:
        last_sync = '从未同步'
    current_time = status['current_time']
    return jsonify({
        'running': status['running'],
        'host': status['host'],
        'port': status['port'],
        'time_offset': f"{status['time_offset']:.6f}",
        'last_sync_time': last_sync,
        'current_time': current_time,
        'client_stats': status['client_stats']
    })

@app.route('/api/sync', methods=['POST'])
def manual_sync():
    """手动同步时间"""
    if ntp_server is None:
        return jsonify({'error': 'NTP服务器未启动'})
    
    success = ntp_server.sync_time()
    return jsonify({
        'success': success,
        'message': '时间同步完成' if success else '时间同步失败'
    })

@app.route('/api/start', methods=['POST'])
def start_server():
    """启动NTP服务器"""
    global ntp_server, server_thread
    
    if ntp_server and ntp_server.running:
        return jsonify({'error': 'NTP服务器已在运行'})
    
    try:
        server_thread = threading.Thread(target=start_ntp_server, daemon=True)
        server_thread.start()
        
        # 等待服务器启动
        time.sleep(2)
        
        return jsonify({'success': True, 'message': 'NTP服务器启动成功'})
    except Exception as e:
        return jsonify({'error': f'启动失败: {str(e)}'})

@app.route('/api/stop', methods=['POST'])
def stop_server():
    """停止NTP服务器"""
    global ntp_server
    
    if ntp_server is None or not ntp_server.running:
        return jsonify({'error': 'NTP服务器未运行'})
    
    try:
        ntp_server.stop()
        return jsonify({'success': True, 'message': 'NTP服务器已停止'})
    except Exception as e:
        return jsonify({'error': f'停止失败: {str(e)}'})

if __name__ == '__main__':
    # 创建templates目录
    import os
    os.makedirs('templates', exist_ok=True)
    
    # 创建静态文件目录
    os.makedirs('static', exist_ok=True)
    
    print("NTP服务器Web管理界面启动中...")
    print("访问 http://localhost:5000 查看管理界面")
    print("按 Ctrl+C 停止服务")
    
    # 检查是否为生产环境
    production_mode = os.environ.get('FLASK_ENV') == 'production'
    
    if production_mode:
        # 生产环境配置
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    else:
        # 开发环境配置
        app.run(host='0.0.0.0', port=5000, debug=False) 