@echo off
chcp 65001 >nul
title NTP校时服务器启动器

echo.
echo ========================================
echo           NTP校时服务器启动器
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.7+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查依赖
echo 检查依赖包...
python -c "import ntplib, flask, requests" >nul 2>&1
if errorlevel 1 (
    echo 安装依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo 错误: 依赖安装失败
        pause
        exit /b 1
    )
)

echo.
echo 选择启动模式:
echo 1. Web管理界面 (推荐)
echo 2. 直接运行NTP服务器
echo 3. 测试NTP服务器
echo 4. 退出
echo.

set /p choice=请输入选择 (1-4): 

if "%choice%"=="1" (
    echo.
    echo 启动Web管理界面...
    echo 访问地址: http://localhost:5000
    echo 按 Ctrl+C 停止服务
    echo.
    python web_interface.py
) else if "%choice%"=="2" (
    echo.
    echo 直接启动NTP服务器...
    echo 按 Ctrl+C 停止服务
    echo.
    python ntp_server.py
) else if "%choice%"=="3" (
    echo.
    echo 启动NTP服务器测试...
    python ntp_client_test.py
    echo.
    pause
) else if "%choice%"=="4" (
    echo 退出
) else (
    echo 无效选择
    pause
) 