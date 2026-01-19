"""
恐慌点扫描相关API
"""
from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict, Any
import os
import json
import pandas as pd
from datetime import datetime
from pathlib import Path

router = APIRouter(prefix="/api/panic-scan", tags=["panic-scan"])


@router.get("/list")
async def list_scan_results():
    """
    列出所有可用的扫描结果文件（按日期排序）
    """
    try:
        # 获取项目根目录
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent
        output_dir = project_root / "output"
        
        if not output_dir.exists():
            return {
                "success": True,
                "files": [],
                "message": "output目录不存在"
            }
        
        # 查找所有恐慌点扫描结果文件
        csv_files = list(output_dir.glob("daily_panic_candidates_*.csv"))
        json_files = list(output_dir.glob("daily_panic_candidates_*.json"))
        
        # 合并并提取日期
        all_files = []
        for f in csv_files + json_files:
            # 从文件名提取日期：daily_panic_candidates_YYYYMMDD.csv
            date_str = f.stem.split("_")[-1]
            try:
                date_obj = datetime.strptime(date_str, "%Y%m%d")
                all_files.append({
                    "filename": f.name,
                    "date": date_obj.strftime("%Y-%m-%d"),
                    "date_obj": date_obj,
                    "type": "csv" if f.suffix == ".csv" else "json",
                    "size": f.stat().st_size
                })
            except ValueError:
                continue
        
        # 按日期倒序排序
        all_files.sort(key=lambda x: x["date_obj"], reverse=True)
        
        return {
            "success": True,
            "files": [
                {
                    "filename": f["filename"],
                    "date": f["date"],
                    "type": f["type"],
                    "size": f["size"]
                }
                for f in all_files
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"列出扫描结果失败: {str(e)}")


@router.get("/latest")
async def get_latest_scan_result():
    """
    获取最新的扫描结果
    """
    try:
        # 获取项目根目录
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent
        output_dir = project_root / "output"
        
        if not output_dir.exists():
            raise HTTPException(status_code=404, detail="output目录不存在")
        
        # 查找最新的CSV文件
        csv_files = list(output_dir.glob("daily_panic_candidates_*.csv"))
        if not csv_files:
            raise HTTPException(status_code=404, detail="未找到扫描结果文件")
        
        # 按修改时间排序，取最新的
        latest_file = max(csv_files, key=lambda f: f.stat().st_mtime)
        
        # 读取CSV文件
        df = pd.read_csv(latest_file, encoding="utf-8-sig")
        
        # 转换为字典列表
        records = df.to_dict("records")
        
        # 提取日期
        date_str = latest_file.stem.split("_")[-1]
        date_obj = datetime.strptime(date_str, "%Y%m%d")
        
        return {
            "success": True,
            "date": date_obj.strftime("%Y-%m-%d"),
            "filename": latest_file.name,
            "count": len(records),
            "records": records
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取最新扫描结果失败: {str(e)}")


@router.get("/by-date/{date}")
async def get_scan_result_by_date(date: str):
    """
    根据日期获取扫描结果（格式：YYYY-MM-DD 或 YYYYMMDD）
    """
    try:
        # 解析日期格式
        try:
            if len(date) == 8:
                date_obj = datetime.strptime(date, "%Y%m%d")
            else:
                date_obj = datetime.strptime(date, "%Y-%m-%d")
            date_str = date_obj.strftime("%Y%m%d")
        except ValueError:
            raise HTTPException(status_code=400, detail=f"日期格式错误: {date}")
        
        # 获取项目根目录
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent
        output_dir = project_root / "output"
        csv_file = output_dir / f"daily_panic_candidates_{date_str}.csv"
        json_file = output_dir / f"daily_panic_candidates_{date_str}.json"
        
        # 优先读取CSV，如果没有则读取JSON
        if csv_file.exists():
            df = pd.read_csv(csv_file, encoding="utf-8-sig")
            records = df.to_dict("records")
            return {
                "success": True,
                "date": date_obj.strftime("%Y-%m-%d"),
                "filename": csv_file.name,
                "count": len(records),
                "records": records
            }
        elif json_file.exists():
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            # 脚本输出的是 orient="records"，直接是列表格式
            if isinstance(data, list):
                records = data
            else:
                records = data.get("records", [])
            return {
                "success": True,
                "date": date_obj.strftime("%Y-%m-%d"),
                "filename": json_file.name,
                "count": len(records),
                "records": records
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"未找到日期为 {date_obj.strftime('%Y-%m-%d')} 的扫描结果"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取扫描结果失败: {str(e)}")


@router.post("/trigger")
async def trigger_scan(
    days: Optional[int] = 300,
    panic_window: Optional[int] = 60,
    recent_days: Optional[int] = 5,
    top_k: Optional[int] = 50,
):
    """
    触发一次恐慌点扫描（在独立进程中执行，立即返回）。
    """
    try:
        import subprocess
        import sys
        import traceback

        # 从当前文件路径推导项目根目录：server/routers/panic_scan.py -> 项目根目录
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent
        script_path = project_root / "scripts" / "daily_panic_scan.py"

        if not script_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"扫描脚本不存在: {script_path}",
            )

        cmd = [
            sys.executable,
            str(script_path),
            "--output-dir",
            str(project_root / "output"),
            "--days",
            str(days),
            "--panic-window",
            str(panic_window),
            "--recent-days",
            str(recent_days),
            "--top-k",
            str(top_k),
        ]

        # 启动子进程，不等待完成
        subprocess.Popen(
            cmd,
            cwd=str(project_root),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        return {
            "success": True,
            "message": "扫描任务已启动",
        }
    except HTTPException:
        raise
    except Exception as e:
        error_detail = f"触发扫描失败: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

