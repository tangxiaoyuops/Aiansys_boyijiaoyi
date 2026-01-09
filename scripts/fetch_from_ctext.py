"""
从中国哲学书电子化计划（Chinese Text Project）获取《黄帝内经》完整文本
这是最可靠的公开古籍资源
"""
import os
import sys
import requests
from pathlib import Path
from bs4 import BeautifulSoup
import re
import time

project_root = Path(__file__).parent.parent
raw_dir = project_root / "data" / "huangdi_neijing" / "raw"
raw_dir.mkdir(parents=True, exist_ok=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# 中国哲学书电子化计划的URL
CTEXT_BASE = "http://ctext.org"
SUWEN_URL = "http://ctext.org/huangdi-neijing/suwen"
LINGSHU_URL = "http://ctext.org/huangdi-neijing/lingshu"


def fetch_from_ctext(url: str, book_name: str) -> str:
    """
    从ctext.org获取文本内容
    
    Args:
        url: 页面URL
        book_name: 书籍名称（用于日志）
        
    Returns:
        提取的文本内容
    """
    print(f"正在从 ctext.org 获取《{book_name}》...")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            print(f"[失败] HTTP状态码: {response.status_code}")
            return ""
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取正文内容
        # ctext.org的页面结构可能包含在特定的div中
        content_divs = soup.find_all(['div', 'p'], class_=re.compile(r'text|content|main'))
        
        text_parts = []
        
        # 如果没有找到特定class，尝试提取所有文本
        if not content_divs:
            # 查找包含"篇"、"章"等关键词的内容
            all_text = soup.get_text()
            text_parts.append(all_text)
        else:
            for div in content_divs:
                text = div.get_text(strip=True)
                if text and len(text) > 10:  # 过滤太短的文本
                    text_parts.append(text)
        
        full_text = '\n\n'.join(text_parts)
        
        # 清理文本
        full_text = re.sub(r'\s+', '\n', full_text)  # 合并多个空白
        full_text = re.sub(r'\n{3,}', '\n\n', full_text)  # 合并多个换行
        
        print(f"[成功] 获取到 {len(full_text)} 字符")
        return full_text
        
    except Exception as e:
        print(f"[失败] 错误: {e}")
        return ""


def fetch_suwen_from_ctext() -> bool:
    """从ctext.org获取素问"""
    content = fetch_from_ctext(SUWEN_URL, "素问")
    
    if content and len(content) > 1000:
        suwen_file = raw_dir / "suwen.txt"
        with open(suwen_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[成功] 素问已保存到: {suwen_file}")
        print(f"  文件大小: {suwen_file.stat().st_size} bytes")
        return True
    else:
        print("[失败] 未能获取到足够的素问内容")
        return False


def fetch_lingshu_from_ctext() -> bool:
    """从ctext.org获取灵枢"""
    content = fetch_from_ctext(LINGSHU_URL, "灵枢")
    
    if content and len(content) > 1000:
        lingshu_file = raw_dir / "lingshu.txt"
        with open(lingshu_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[成功] 灵枢已保存到: {lingshu_file}")
        print(f"  文件大小: {lingshu_file.stat().st_size} bytes")
        return True
    else:
        print("[失败] 未能获取到足够的灵枢内容")
        return False


def create_direct_download_guide():
    """创建直接下载指南"""
    guide = raw_dir / "从CTEXT下载指南.md"
    content = """# 从中国哲学书电子化计划获取《黄帝内经》完整文本

## 推荐方法（最可靠）

### 方法1: 直接从网站获取

1. **访问素问**:
   - URL: http://ctext.org/huangdi-neijing/suwen
   - 在页面上选择"显示原文"
   - 复制所有文本内容
   - 保存为 `suwen.txt` (UTF-8编码)

2. **访问灵枢**:
   - URL: http://ctext.org/huangdi-neijing/lingshu
   - 在页面上选择"显示原文"
   - 复制所有文本内容
   - 保存为 `lingshu.txt` (UTF-8编码)

3. **保存位置**:
   ```
   data/huangdi_neijing/raw/suwen.txt
   data/huangdi_neijing/raw/lingshu.txt
   ```

### 方法2: 使用浏览器扩展

可以使用浏览器扩展（如"Copy All URLs"）批量下载所有章节。

### 方法3: 使用Python脚本（需要调整）

由于ctext.org的页面结构可能变化，建议手动访问网站获取。

## 其他可靠来源

1. **中国古籍网**: https://www.guoxue.com/
2. **国学网**: https://www.guoxue.com/
3. **古籍在线**: https://www.guji.cn/

## 文件格式要求

- 编码: UTF-8
- 格式: 每篇以 `## 第X篇 篇名` 开头（推荐）
- 或保持原始格式，系统会自动解析

## 验证

获取后运行:
```bash
python core/tools/init_huangdi_kb.py
```

这将重新处理文本并构建向量数据库。
"""
    
    with open(guide, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"[指南] 已创建下载指南: {guide}")


def main():
    """主函数"""
    print("=" * 70)
    print("从中国哲学书电子化计划获取《黄帝内经》")
    print("=" * 70)
    print()
    
    print("注意: ctext.org可能需要手动访问获取完整内容")
    print("推荐直接访问网站手动复制文本")
    print()
    
    # 尝试自动获取
    print("尝试自动获取...")
    suwen_ok = fetch_suwen_from_ctext()
    time.sleep(2)  # 避免请求过快
    
    lingshu_ok = fetch_lingshu_from_ctext()
    
    print()
    print("=" * 70)
    print("获取结果")
    print("=" * 70)
    print(f"素问: {'[成功]' if suwen_ok else '[失败]'}")
    print(f"灵枢: {'[成功]' if lingshu_ok else '[失败]'}")
    
    if not suwen_ok or not lingshu_ok:
        print()
        print("自动获取失败，请手动操作:")
        print("1. 访问: http://ctext.org/huangdi-neijing/suwen")
        print("2. 访问: http://ctext.org/huangdi-neijing/lingshu")
        print("3. 复制文本内容并保存")
        create_direct_download_guide()
    else:
        print()
        print("[成功] 文本已获取！")
        print("下一步: 运行 python core/tools/init_huangdi_kb.py 初始化知识库")


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

