# NTP校时服务器

一个功能完整的NTP（Network Time Protocol）校时服务器，支持从多个公共NTP服务器获取最新时间，并为客户端提供校时服务。

## 功能特性

- 🕐 **多源时间同步**: 从多个公共NTP服务器获取时间，确保准确性
- 🔄 **自动同步**: 定期自动同步时间，保持时间精度
- 🌐 **客户端服务**: 为NTP客户端提供标准的校时服务
- 📊 **Web管理界面**: 现代化的Web界面，实时监控服务器状态
- 📈 **连接统计**: 统计客户端连接数量和活跃状态
- 🛠️ **手动控制**: 支持手动启动、停止和同步操作
- 📝 **详细日志**: 完整的操作日志记录
- 🚀 **生产就绪**: 支持生产环境部署

## 系统要求

- Python 3.7+
- Windows/Linux/macOS

## 安装步骤

1. **克隆或下载项目**
   ```bash
   git clone <repository-url>
   cd ntp校时服务器
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **快速测试功能**
   ```bash
   python quick_test.py
   ```

4. **启动Web管理界面**
   ```bash
   python web_interface.py
   ```

5. **访问管理界面**
   打开浏览器访问: http://localhost:5000

## 使用方法

### 方法一：使用Web管理界面（推荐）

1. **开发环境启动**：
   ```bash
   python web_interface.py
   ```

2. **生产环境启动**：
   ```bash
   python start_production.py
   ```

3. 在浏览器中访问 http://localhost:5000

4. 点击"启动服务器"按钮启动NTP服务

5. 通过界面监控服务器状态和管理服务

### 方法二：直接运行NTP服务器

```bash
python ntp_server.py
```

### 方法三：使用启动脚本

**Windows用户**：
```bash
start.bat
```

**所有平台**：
```bash
python start_server.py
```

### 方法四：测试服务器功能

```bash
# 快速功能测试
python quick_test.py

# 测试本地NTP服务器
python ntp_client_test.py

# 测试指定服务器
python ntp_client_test.py 192.168.1.100

# 与公共NTP服务器对比测试
python ntp_client_test.py --compare
```

## 配置说明

### NTP服务器配置

在 `ntp_server.py` 中可以修改以下配置：

```python
# 服务器监听地址和端口
host = '0.0.0.0'  # 监听所有网络接口
port = 123        # 标准NTP端口

# 时间同步间隔（秒）
sync_interval = 300  # 5分钟同步一次

# 公共NTP服务器列表
ntp_servers = [
    'time.windows.com',
    'time.nist.gov', 
    'pool.ntp.org',
    'time.google.com',
    'time.apple.com'
]
```

### Web界面配置

在 `web_interface.py` 中可以修改Web服务配置：

```python
# 开发环境配置
app.run(host='0.0.0.0', port=5000, debug=False)

# 生产环境配置（使用WSGI服务器）
serve(app, host='0.0.0.0', port=5000, threads=4)
```

### 生产环境部署

1. **使用WSGI服务器**：
   ```bash
   python start_production.py
   ```

2. **设置环境变量**：
   ```bash
   export FLASK_ENV=production
   python web_interface.py
   ```

3. **使用系统服务**：
   ```bash
   # 创建systemd服务文件
   sudo nano /etc/systemd/system/ntp-server.service
   ```

## 文件结构

```
ntp校时服务器/
├── ntp_server.py          # 主NTP服务器
├── web_interface.py       # Web管理界面
├── ntp_client_test.py     # 客户端测试工具
├── quick_test.py          # 快速功能测试
├── start_server.py        # 通用启动脚本
├── start_production.py    # 生产环境启动脚本
├── start.bat             # Windows启动脚本
├── requirements.txt       # Python依赖
├── README.md             # 项目说明
├── templates/
│   └── index.html        # Web界面模板
└── ntp_server.log        # 服务器日志（运行时生成）
```

## 技术特性

### 时间同步算法

1. **多源查询**: 同时查询多个公共NTP服务器
2. **异常过滤**: 过滤异常的时间偏移值
3. **中位数选择**: 使用中位数作为最终偏移量，避免异常值影响
4. **定期更新**: 每5分钟自动同步一次时间

### NTP协议实现

- 支持NTP v3协议
- 标准48字节数据包格式
- 完整的时间戳处理
- 网络延迟补偿

### 并发处理

- 多线程处理客户端连接
- 线程安全的状态管理
- 非阻塞的I/O操作

### 生产环境特性

- WSGI服务器支持（waitress）
- 生产级错误处理
- 性能优化配置
- 安全最佳实践

## 故障排除

### 常见问题

1. **端口被占用**
   ```
   错误: [Errno 98] Address already in use
   解决: 修改端口号或停止占用端口的程序
   ```

2. **权限不足**
   ```
   错误: [Errno 13] Permission denied
   解决: 使用管理员权限运行或修改端口号
   ```

3. **网络连接失败**
   ```
   错误: 无法连接到NTP服务器
   解决: 检查网络连接和防火墙设置
   ```

4. **Flask开发服务器警告**
   ```
   警告: This is a development server...
   解决: 使用 start_production.py 启动生产环境
   ```

### 日志查看

服务器运行时会生成 `ntp_server.log` 日志文件，包含详细的操作记录：

```bash
tail -f ntp_server.log
```

### 快速诊断

运行快速测试脚本检查基本功能：

```bash
python quick_test.py
```

## 安全注意事项

1. **防火墙配置**: 确保UDP端口123开放（NTP服务）
2. **网络访问**: 根据需要限制Web管理界面的访问范围
3. **权限管理**: 在生产环境中使用适当的用户权限运行服务
4. **HTTPS**: 在生产环境中配置HTTPS加密

## 性能优化

1. **同步间隔**: 根据网络环境调整同步间隔
2. **服务器选择**: 选择网络延迟较低的NTP服务器
3. **并发连接**: 根据服务器性能调整最大并发连接数
4. **WSGI服务器**: 使用生产级WSGI服务器提升性能

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 提交GitHub Issue
- 发送邮件至项目维护者

---

**注意**: 在生产环境中使用前，请充分测试并确保符合相关安全要求。 