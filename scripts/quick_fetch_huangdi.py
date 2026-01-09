"""
快速获取《黄帝内经》完整文本
简化版本，直接提供获取方法
"""
import os
import sys
from pathlib import Path

# 项目根目录
project_root = Path(__file__).parent.parent
raw_dir = project_root / "data" / "huangdi_neijing" / "raw"
raw_dir.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("《黄帝内经》完整文本获取工具")
print("=" * 70)
print()

# 检查现有文件
suwen_file = raw_dir / "suwen.txt"
lingshu_file = raw_dir / "lingshu.txt"
suwen_complete = raw_dir / "suwen_complete.txt"

print("检查现有文件...")
if suwen_complete.exists() and suwen_complete.stat().st_size > 1000:
    print(f"[OK] 发现完整素问文件: {suwen_complete}")
    print(f"  正在复制到: {suwen_file}")
    with open(suwen_complete, 'r', encoding='utf-8') as f_in:
        with open(suwen_file, 'w', encoding='utf-8') as f_out:
            f_out.write(f_in.read())
        print(f"  [OK] 素问文件已就绪 ({suwen_file.stat().st_size} bytes)")
elif suwen_file.exists():
    size = suwen_file.stat().st_size
    if size > 10000:
        print(f"[OK] 素问文件已存在 ({size} bytes)")
    else:
        print(f"[WARN] 素问文件存在但可能不完整 ({size} bytes)")
else:
    print("[ERROR] 未找到素问文件")

if lingshu_file.exists():
    size = lingshu_file.stat().st_size
    if size > 10000:
        print(f"[OK] 灵枢文件已存在 ({size} bytes)")
    else:
        print(f"[WARN] 灵枢文件存在但可能不完整 ({size} bytes)")
else:
    print("[ERROR] 未找到灵枢文件")

print()
print("=" * 70)
print("获取完整文本的方法")
print("=" * 70)
print()
print("方法1: 从GitHub获取（推荐）")
print("  1. 访问: https://github.com/garychowcmu/ChineseText")
print("  2. 找到 黄帝内经 目录")
print("  3. 下载 素问.txt 和 灵枢.txt")
print("  4. 保存到: data/huangdi_neijing/raw/")
print()
print("方法2: 从古籍网站下载")
print("  - 中国古籍网: https://www.guoxue.com/")
print("  - 搜索'黄帝内经'，下载TXT格式")
print()
print("方法3: 使用搜索引擎")
print("  搜索: '黄帝内经 素问 灵枢 txt 下载'")
print()
print("文件要求:")
print("  - 文件名: suwen.txt 和 lingshu.txt")
print("  - 编码: UTF-8")
print("  - 位置: data/huangdi_neijing/raw/")
print()
print("获取后运行初始化:")
print("  python core/tools/init_huangdi_kb.py")
print()

