@echo off
chcp 65001 >nul
echo ========================================
echo 启动博弈交易分析系统（集成Agent框架）
echo ========================================
echo.
echo 正在启动后端服务...
echo 端口: 8000
echo API文档: http://localhost:8000/docs
echo.

python -m uvicorn server.app:app --host 0.0.0.0 --port 8000

pause
