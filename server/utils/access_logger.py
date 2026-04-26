"""
访问日志工具模块
记录用户访问日志到文件
"""
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any
import socket


# 日志存储目录
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "access")


def ensure_log_dir():
    """确保日志目录存在"""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR, exist_ok=True)


def get_client_ip(request) -> str:
    """获取客户端真实IP"""
    # 尝试从各种头部获取真实IP
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # 直接连接的IP
    if hasattr(request, "client") and request.client:
        return request.client.host
    
    return "unknown"


def get_log_filename() -> str:
    """获取当天的日志文件名"""
    today = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(LOG_DIR, f"access_{today}.log")


def log_access(
    request,
    response_status: int = 200,
    response_time_ms: Optional[float] = None,
    extra_info: Optional[Dict[str, Any]] = None
) -> None:
    """
    记录访问日志
    
    Args:
        request: FastAPI请求对象
        response_status: 响应状态码
        response_time_ms: 响应时间(毫秒)
        extra_info: 额外信息
    """
    ensure_log_dir()
    
    now = datetime.now()

    # 构建日志记录
    log_entry = {
        "timestamp": now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
        "timestamp_iso": now.isoformat(timespec="milliseconds"),
        "timestamp_unix": now.timestamp(),
        "client_ip": get_client_ip(request),
        "method": request.method,
        "path": request.url.path,
        "query_params": dict(request.query_params) if request.query_params else {},
        "status_code": response_status,
        "user_agent": request.headers.get("User-Agent", ""),
        "referer": request.headers.get("Referer", ""),
        "host": request.headers.get("Host", ""),
        "response_time_ms": round(response_time_ms, 2) if response_time_ms else None,
    }
    
    # 添加额外信息
    if extra_info:
        log_entry["extra"] = extra_info
    
    # 写入日志文件
    log_file = get_log_filename()
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"[访问日志] 写入日志失败: {e}")
    
    # 同时打印到控制台
    print(f"[访问日志] {log_entry['timestamp']} | {log_entry['client_ip']} | "
          f"{log_entry['method']} {log_entry['path']} | {log_entry['status_code']} | "
          f"{log_entry['response_time_ms']}ms")


def log_page_view(page_name: str, user_info: Optional[Dict[str, Any]] = None) -> None:
    """
    记录页面访问（前端调用）
    
    Args:
        page_name: 页面名称
        user_info: 用户信息
    """
    ensure_log_dir()
    
    now = datetime.now()

    log_entry = {
        "timestamp": now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
        "timestamp_iso": now.isoformat(timespec="milliseconds"),
        "timestamp_unix": now.timestamp(),
        "type": "page_view",
        "page": page_name,
        "user_info": user_info or {},
    }
    
    log_file = get_log_filename()
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"[访问日志] 写入日志失败: {e}")
    
    print(f"[页面访问] {log_entry['timestamp']} | {page_name}")
