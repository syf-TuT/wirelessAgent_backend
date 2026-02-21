@echo off
echo ========================================
echo 安装前端依赖
echo ========================================
echo.

cd /d F:\code\wirelessAgent_backend\wirelessagent-frontend

echo 正在安装npm依赖...
call npm install

if %errorlevel% neq 0 (
    echo.
    echo 依赖安装失败！
    pause
    exit /b 1
)

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 现在可以运行 start.bat 启动系统
echo.
pause
