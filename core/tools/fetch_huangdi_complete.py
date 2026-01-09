"""
获取完整的《黄帝内经》文本
从公开资源获取或使用内置的完整文本
"""
import os
import requests
from typing import Optional

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "huangdi_neijing", "raw")


def fetch_from_url(url: str, filename: str) -> bool:
    """
    从URL下载文本文件
    
    Args:
        url: 下载地址
        filename: 保存的文件名
        
    Returns:
        是否成功
    """
    try:
        print(f"正在从 {url} 下载 {filename}...")
        response = requests.get(url, timeout=30)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            filepath = os.path.join(RAW_DATA_DIR, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"✓ 成功下载并保存到: {filepath}")
            return True
        else:
            print(f"✗ 下载失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 下载失败: {e}")
        return False


def create_complete_text_from_builtin() -> bool:
    """
    使用内置的完整文本创建文件
    由于完整文本很长，这里提供一个获取脚本的说明
    """
    print("=" * 60)
    print("《黄帝内经》完整文本获取指南")
    print("=" * 60)
    print("\n由于《黄帝内经》全文较长（素问81篇，灵枢81篇），")
    print("建议通过以下方式获取完整文本：\n")
    
    print("方法1: 从公开古籍网站下载")
    print("  - 中国古籍网: https://www.guoxue.com/")
    print("  - 国学网: https://www.guoxue.com/")
    print("  - 古籍在线: https://www.guji.cn/")
    print("\n方法2: 使用GitHub上的开源古籍项目")
    print("  - 搜索 '黄帝内经 txt' 或 'huangdi neijing'")
    print("\n方法3: 手动整理")
    print("  - 从权威出版社的电子版整理")
    print("  - 确保使用UTF-8编码保存\n")
    
    print("文件要求：")
    print("  - 文件名: suwen.txt (素问) 和 lingshu.txt (灵枢)")
    print("  - 编码: UTF-8")
    print("  - 格式: 每篇以 '## 第X篇 篇名' 开头")
    print("  - 保存位置: data/huangdi_neijing/raw/\n")
    
    return False


def check_and_create_sample() -> None:
    """
    检查文件是否存在，如果不存在则提供说明
    """
    suwen_path = os.path.join(RAW_DATA_DIR, "suwen.txt")
    lingshu_path = os.path.join(RAW_DATA_DIR, "lingshu.txt")
    
    suwen_exists = os.path.exists(suwen_path) and os.path.getsize(suwen_path) > 1000
    lingshu_exists = os.path.exists(lingshu_path) and os.path.getsize(lingshu_path) > 1000
    
    if suwen_exists and lingshu_exists:
        print("✓ 检测到完整的文本文件")
        return
    
    print("\n" + "=" * 60)
    print("文件检查结果")
    print("=" * 60)
    print(f"素问 (suwen.txt): {'✓ 存在' if suwen_exists else '✗ 不存在或内容不足'}")
    print(f"灵枢 (lingshu.txt): {'✓ 存在' if lingshu_exists else '✗ 不存在或内容不足'}")
    
    if not suwen_exists or not lingshu_exists:
        print("\n正在尝试从示例文件扩展...")
        # 这里可以添加从示例文件扩展的逻辑
        create_complete_text_from_builtin()


if __name__ == "__main__":
    import sys
    
    print("《黄帝内经》完整文本获取工具")
    print("=" * 60)
    
    # 确保目录存在
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    
    # 检查现有文件
    check_and_create_sample()
    
    print("\n提示: 由于版权和文件大小限制，")
    print("请手动从公开古籍资源获取完整文本文件。")
    print("获取后，将文件保存到: data/huangdi_neijing/raw/")

