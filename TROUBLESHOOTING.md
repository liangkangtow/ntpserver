# NTP校时服务器故障排除指南

## 常见问题及解决方案

### 1. Flask环境变量错误

**错误信息**：
```
KeyError: 'WERKZEUG_SERVER_FD'
```

**解决方案**：
- 使用简化启动脚本：`python simple_start.py`
- 或者直接运行：`python web_interface.py`

### 2. 端口被占用

**错误信息**：
```
[Errno 98] Address already in use
```

**解决方案**：
- 检查端口占用：`netstat -an | grep :5000`
- 停止占用端口的程序
- 或者修改端口号

### 3. 权限不足

**错误信息**：
```
[Errno 13] Permission denied
```

**解决方案**：
- Windows：以管理员身份运行
- Linux/macOS：使用sudo或修改端口号

### 4. 依赖包缺失

**错误信息**：
```
ModuleNotFoundError: No module named 'xxx'
```

**解决方案**：
```bash
pip install -r requirements.txt
```

### 5. NTP服务器无法启动

**可能原因**：
- 端口123被系统NTP服务占用
- 防火墙阻止连接

**解决方案**：
- 修改端口号（在ntp_server.py中）
- 检查防火墙设置
- 停止系统NTP服务

### 6. 时间同步失败

**可能原因**：
- 网络连接问题
- 公共NTP服务器不可达

**解决方案**：
- 检查网络连接
- 尝试手动同步
- 更换NTP服务器

## 启动方式选择

### 推荐启动方式

1. **首次使用**：
   ```bash
   python simple_start.py
   ```

2. **直接启动**：
   ```bash
   python web_interface.py
   ```

3. **生产环境**：
   ```bash
   python start_production.py
   ```

4. **Windows用户**：
   ```bash
   start.bat
   ```

## 测试和诊断

### 快速测试
```bash
python quick_test.py
```

### 客户端测试
```bash
python ntp_client_test.py
```

### 查看日志
```bash
tail -f ntp_server.log
```

## 配置修改

### 修改端口号
编辑 `ntp_server.py`：
```python
def __init__(self, host='0.0.0.0', port=12345, sync_interval=300):
```

### 修改同步间隔
```python
def __init__(self, host='0.0.0.0', port=123, sync_interval=600):  # 10分钟
```

### 添加NTP服务器
```python
self.ntp_servers = [
    'time.windows.com',
    'time.nist.gov',
    'pool.ntp.org',
    'time.google.com',
    'time.apple.com',
    'your.ntp.server'  # 添加自定义服务器
]
```

## 性能优化

### 减少同步频率
```python
sync_interval = 600  # 10分钟同步一次
```

### 增加并发连接
```python
self.server_socket.listen(10)  # 增加连接队列
```

### 使用生产级WSGI服务器
```bash
python start_production.py
```

## 安全建议

1. **防火墙配置**
   - 只开放必要的端口
   - 限制访问来源

2. **网络隔离**
   - 在内网环境中使用
   - 避免直接暴露到公网

3. **日志监控**
   - 定期检查日志文件
   - 监控异常连接

## 联系支持

如果问题仍然存在，请：
1. 运行 `python quick_test.py` 获取诊断信息
2. 查看 `ntp_server.log` 日志文件
3. 提供错误信息和系统环境 