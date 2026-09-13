"""
通用自主规划Agent框架 - 启动脚本
快速启动Web服务
"""
import sys
import os
import subprocess

def check_dependencies():
    """检查依赖"""
    print("="*60)
    print("检查依赖...")
    print("="*60)
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'openai',
        'pydantic',
        'requests'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"[OK] {package}")
        except ImportError:
            print(f"[X] {package} (missing)")
            missing.append(package)
    
    if missing:
        print("\n缺少以下依赖:")
        for pkg in missing:
            print(f"  - {pkg}")
        print("\n请运行以下命令安装:")
        print(f"  pip install {' '.join(missing)}")
        return False
    
    print("\n[OK] All dependencies installed")
    return True


def start_server():
    """启动服务器"""
    print("\n" + "="*60)
    print("启动Agent框架服务...")
    print("="*60)
    print("\n服务地址:")
    print("  - Web界面: http://localhost:8001/ui")
    print("  - API文档: http://localhost:8001/docs")
    print("  - 健康检查: http://localhost:8001/api/health")
    print("\n按 Ctrl+C 停止服务")
    print("="*60 + "\n")
    
    # 启动uvicorn - 使用8001端口避免冲突
    subprocess.run([
        sys.executable, '-m', 'uvicorn',
        'core.agent_framework.api.app:app',
        '--host', '0.0.0.0',
        '--port', '8001',
        '--reload'
    ])


if __name__ == "__main__":
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 启动服务
    start_server()
