"""
获取完整的《黄帝内经》文本
从多个公开资源获取或合并现有文件
"""
import os
import sys
from typing import Optional

import requests
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

RAW_DATA_DIR = project_root / "data" / "huangdi_neijing" / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_huangdi_from_github() -> tuple[Optional[str], Optional[str]]:
    """
    尝试从GitHub获取《黄帝内经》文本
    
    Returns:
        (suwen_text, lingshu_text)
    """
    # 一些可能的GitHub资源
    github_urls = [
        "https://raw.githubusercontent.com/garychowcmu/ChineseText/master/黄帝内经/素问.txt",
        "https://raw.githubusercontent.com/garychowcmu/ChineseText/master/黄帝内经/灵枢.txt",
    ]
    
    suwen_text = None
    lingshu_text = None
    
    try:
        # 尝试获取素问
        for url in github_urls:
            if "素问" in url or "suwen" in url.lower():
                print(f"正在尝试从GitHub获取素问: {url}")
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    suwen_text = response.text
                    print("✓ 成功获取素问")
                    break
        
        # 尝试获取灵枢
        for url in github_urls:
            if "灵枢" in url or "lingshu" in url.lower():
                print(f"正在尝试从GitHub获取灵枢: {url}")
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    lingshu_text = response.text
                    print("✓ 成功获取灵枢")
                    break
    except Exception as e:
        print(f"从GitHub获取失败: {e}")
    
    return suwen_text, lingshu_text


def merge_sample_files() -> None:
    """
    合并现有的示例文件，创建更完整的内容
    """
    suwen_sample = RAW_DATA_DIR / "suwen_sample.txt"
    suwen_complete = RAW_DATA_DIR / "suwen_complete.txt"
    suwen_output = RAW_DATA_DIR / "suwen.txt"
    
    lingshu_sample = RAW_DATA_DIR / "lingshu_sample.txt"
    lingshu_output = RAW_DATA_DIR / "lingshu.txt"
    
    # 处理素问
    if suwen_complete.exists() and suwen_complete.stat().st_size > 1000:
        print(f"使用现有的完整素问文件: {suwen_complete}")
        with open(suwen_complete, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(suwen_output, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ 素问文件已保存到: {suwen_output}")
    elif suwen_sample.exists():
        print(f"使用示例素问文件: {suwen_sample}")
        with open(suwen_sample, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(suwen_output, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ 素问示例文件已复制到: {suwen_output}")
        print("  注意: 这是示例文件，内容不完整，请手动补充完整内容")
    
    # 处理灵枢
    if lingshu_sample.exists():
        print(f"使用示例灵枢文件: {lingshu_sample}")
        with open(lingshu_sample, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(lingshu_output, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ 灵枢示例文件已复制到: {lingshu_output}")
        print("  注意: 这是示例文件，内容不完整，请手动补充完整内容")


def create_download_guide() -> None:
    """
    创建下载指南文件
    """
    guide_file = RAW_DATA_DIR / "DOWNLOAD_GUIDE.md"
    guide_content = """# 《黄帝内经》完整文本获取指南

## 推荐资源

### 1. 公开古籍网站
- **中国古籍网**: https://www.guoxue.com/
- **国学网**: https://www.guoxue.com/
- **古籍在线**: https://www.guji.cn/
- **汉典古籍**: https://www.zdic.net/

### 2. GitHub开源项目
搜索关键词: `黄帝内经 txt` 或 `huangdi neijing`

一些可能的项目:
- https://github.com/garychowcmu/ChineseText
- https://github.com/chinese-poetry/chinese-poetry (可能包含古籍)

### 3. 图书馆资源
- 国家图书馆古籍资源
- 各大学图书馆古籍数据库

## 文件要求

1. **文件名**:
   - `suwen.txt` - 素问（81篇）
   - `lingshu.txt` - 灵枢（81篇）

2. **编码**: UTF-8

3. **格式建议**:
   ```
   ## 第一篇 篇名
   正文内容...
   
   ## 第二篇 篇名
   正文内容...
   ```

4. **保存位置**: `data/huangdi_neijing/raw/`

## 验证完整性

- 素问应有81篇
- 灵枢应有81篇
- 每篇应有完整的标题和内容

## 处理步骤

1. 下载完整文本文件
2. 确保UTF-8编码
3. 保存到指定目录
4. 运行初始化脚本: `python core/tools/init_huangdi_kb.py`
"""
    
    with open(guide_file, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print(f"✓ 下载指南已保存到: {guide_file}")


def main():
    """主函数"""
    print("=" * 60)
    print("《黄帝内经》完整文本获取工具")
    print("=" * 60)
    print()
    
    # 1. 尝试从GitHub获取
    print("步骤1: 尝试从公开资源获取...")
    suwen_text, lingshu_text = get_huangdi_from_github()
    
    if suwen_text:
        suwen_file = RAW_DATA_DIR / "suwen.txt"
        with open(suwen_file, 'w', encoding='utf-8') as f:
            f.write(suwen_text)
        print(f"✓ 素问已保存到: {suwen_file}")
    
    if lingshu_text:
        lingshu_file = RAW_DATA_DIR / "lingshu.txt"
        with open(lingshu_file, 'w', encoding='utf-8') as f:
            f.write(lingshu_text)
        print(f"✓ 灵枢已保存到: {lingshu_file}")
    
    # 2. 合并现有文件
    print("\n步骤2: 检查并合并现有文件...")
    merge_sample_files()
    
    # 3. 创建下载指南
    print("\n步骤3: 创建下载指南...")
    create_download_guide()
    
    print("\n" + "=" * 60)
    print("完成!")
    print("=" * 60)
    print("\n如果自动获取失败，请:")
    print("1. 查看下载指南: data/huangdi_neijing/raw/DOWNLOAD_GUIDE.md")
    print("2. 手动下载完整文本并保存到: data/huangdi_neijing/raw/")
    print("3. 运行初始化脚本: python core/tools/init_huangdi_kb.py")


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

