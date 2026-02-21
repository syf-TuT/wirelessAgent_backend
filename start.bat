@echo off
echo ========================================
echo 5G网络切片资源分配系统 - 启动脚本
echo ========================================
echo.

echo [1/2] 正在启动后端API服务器...
start cmd /k "cd /d F:\code\wirelessAgent_backend && python api_server.py"

echo 等待后端服务器启动...
timeout /t 3 /nobreak >nul

echo.
echo [2/2] 正在启动前端开发服务器...
cd /d F:\code\wirelessAgent_backend\wirelessagent-frontend
start cmd /k "npm run dev"

echo.
echo ========================================
echo 启动完成！
echo ========================================
echo.
echo 后端API: http://localhost:8000
echo 前端界面: http://localhost:5173
echo.
echo API文档: http://localhost:8000/docs
echo.
echo 按任意键关闭此窗口...
pause >nul
