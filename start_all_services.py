"""
同时启动主服务器和Agent框架服务
"""
import subprocess
import time
import sys
import os

# 切换到项目根目录
os.chdir(r'G:\projects\博弈交易\Aiansys_boyijiaoyi')

print("=" * 80)
print("启动博弈交易分析系统")
print("=" * 80)

# 启动主服务器
print("\n[1/2] 启动主服务器 (端口8000)...")
main_server = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT
)

time.sleep(3)

# 启动Agent框架
print("[2/2] 启动Agent框架 (端口8001)...")
agent_server = subprocess.Popen(
    [sys.executable, "core/agent_framework/api/app.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT
)

time.sleep(2)

print("\n" + "=" * 80)
print("✅ 服务启动完成!")
print("=" * 80)
print("\n访问地址:")
print("  主服务器 (端口8000):")
print("    - API文档: http://localhost:8000/docs")
print("    - 股票分析: http://localhost:5173 (前端)")
print("    - 期货分析: http://localhost:5173/futures (前端)")
print("\n  Agent框架 (端口8001):")
print("    - API文档: http://localhost:8001/docs")
print("    - Web界面: http://localhost:8001/ui")
print("\n按 Ctrl+C 停止所有服务")
print("=" * 80)

try:
    # 等待
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n\n正在停止服务...")
    main_server.terminate()
    agent_server.terminate()
    print("✅ 服务已停止")
