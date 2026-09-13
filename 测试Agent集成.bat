@echo off
chcp 65001 >nul
echo ========================================
echo 测试Agent框架集成
echo ========================================
echo.

echo [步骤1] 测试主服务状态...
curl -s http://localhost:8000/api/vnpy/status
echo.
echo.

echo [步骤2] 配置Agent框架...
curl -s -X POST http://localhost:8000/api/agent/config -H "Content-Type: application/json" -d "{}"
echo.
echo.

echo [步骤3] 检查Agent状态...
curl -s http://localhost:8000/api/agent/status
echo.
echo.

echo ========================================
echo 测试完成！
echo ========================================
pause
