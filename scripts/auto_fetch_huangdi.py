"""
自动获取《黄帝内经》完整文本
从多个公开资源尝试下载
"""
import os
import sys
import requests
from pathlib import Path
import time

# 项目根目录
project_root = Path(__file__).parent.parent
raw_dir = project_root / "data" / "huangdi_neijing" / "raw"
raw_dir.mkdir(parents=True, exist_ok=True)

# 设置请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# 可能的资源URL（公开的古籍资源）
RESOURCE_URLS = {
    'suwen': [
        # GitHub资源
        'https://raw.githubusercontent.com/garychowcmu/ChineseText/master/黄帝内经/素问.txt',
        'https://raw.githubusercontent.com/chinese-poetry/chinese-poetry/master/data/黄帝内经/素问.txt',
        # 备用：直接文本内容（如果URL不可用）
    ],
    'lingshu': [
        'https://raw.githubusercontent.com/garychowcmu/ChineseText/master/黄帝内经/灵枢.txt',
        'https://raw.githubusercontent.com/chinese-poetry/chinese-poetry/master/data/黄帝内经/灵枢.txt',
    ]
}


def download_file(url: str, filepath: Path) -> bool:
    """下载文件"""
    try:
        print(f"正在尝试: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        
        if response.status_code == 200 and len(response.text) > 1000:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(response.text)
            size = filepath.stat().st_size
            print(f"[成功] 已下载到: {filepath} ({size} bytes)")
            return True
        else:
            print(f"[失败] 状态码: {response.status_code} 或内容不足")
            return False
    except Exception as e:
        print(f"[失败] 错误: {str(e)[:100]}")
        return False


def create_from_builtin_suwen() -> bool:
    """从内置内容创建素问文件（如果下载失败）"""
    # 这里可以添加一些基础内容，但完整版太长，建议从外部获取
    return False


def create_from_builtin_lingshu() -> bool:
    """从内置内容创建灵枢文件（如果下载失败）"""
    return False


def merge_existing_files():
    """合并现有文件"""
    suwen_complete = raw_dir / "suwen_complete.txt"
    suwen_sample = raw_dir / "suwen_sample.txt"
    suwen_output = raw_dir / "suwen.txt"
    
    lingshu_sample = raw_dir / "lingshu_sample.txt"
    lingshu_output = raw_dir / "lingshu.txt"
    
    # 处理素问
    if suwen_complete.exists() and suwen_complete.stat().st_size > 1000:
        print(f"\n使用现有完整素问文件...")
        with open(suwen_complete, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(suwen_output, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[OK] 素问已就绪: {suwen_output.stat().st_size} bytes")
        return True
    elif suwen_sample.exists():
        print(f"\n使用示例素问文件（内容不完整）...")
        with open(suwen_sample, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(suwen_output, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[WARN] 素问示例已复制（内容不完整）")
    
    # 处理灵枢
    if lingshu_sample.exists():
        print(f"\n使用示例灵枢文件（内容不完整）...")
        with open(lingshu_sample, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(lingshu_output, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[WARN] 灵枢示例已复制（内容不完整）")
    
    return False


def main():
    print("=" * 70)
    print("《黄帝内经》自动获取工具")
    print("=" * 70)
    print()
    
    success_count = 0
    
    # 尝试下载素问
    print("步骤1: 获取《素问》...")
    suwen_file = raw_dir / "suwen.txt"
    if suwen_file.exists() and suwen_file.stat().st_size > 10000:
        print(f"[跳过] 素问文件已存在 ({suwen_file.stat().st_size} bytes)")
        success_count += 1
    else:
        downloaded = False
        for url in RESOURCE_URLS['suwen']:
            if download_file(url, suwen_file):
                downloaded = True
                success_count += 1
                break
            time.sleep(1)  # 避免请求过快
        
        if not downloaded:
            print("[提示] 无法从网络获取，尝试使用现有文件...")
            merge_existing_files()
    
    print()
    
    # 尝试下载灵枢
    print("步骤2: 获取《灵枢》...")
    lingshu_file = raw_dir / "lingshu.txt"
    if lingshu_file.exists() and lingshu_file.stat().st_size > 10000:
        print(f"[跳过] 灵枢文件已存在 ({lingshu_file.stat().st_size} bytes)")
        success_count += 1
    else:
        downloaded = False
        for url in RESOURCE_URLS['lingshu']:
            if download_file(url, lingshu_file):
                downloaded = True
                success_count += 1
                break
            time.sleep(1)
        
        if not downloaded:
            print("[提示] 无法从网络获取，尝试使用现有文件...")
            merge_existing_files()
    
    print()
    print("=" * 70)
    print("获取结果")
    print("=" * 70)
    
    # 检查最终结果
    suwen_ok = suwen_file.exists() and suwen_file.stat().st_size > 1000
    lingshu_ok = lingshu_file.exists() and lingshu_file.stat().st_size > 1000
    
    print(f"素问: {'[OK]' if suwen_ok else '[失败]'}")
    if suwen_ok:
        print(f"  文件: {suwen_file}")
        print(f"  大小: {suwen_file.stat().st_size} bytes")
    
    print(f"灵枢: {'[OK]' if lingshu_ok else '[失败]'}")
    if lingshu_ok:
        print(f"  文件: {lingshu_file}")
        print(f"  大小: {lingshu_file.stat().st_size} bytes")
    
    if suwen_ok and lingshu_ok:
        print()
        print("[成功] 文件已就绪！")
        print("下一步: 运行 python core/tools/init_huangdi_kb.py 初始化知识库")
    else:
        print()
        print("[提示] 部分文件获取失败，请查看获取指南手动下载:")
        print("  data/huangdi_neijing/raw/获取完整文本说明.md")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

