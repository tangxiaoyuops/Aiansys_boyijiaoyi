# 《黄帝内经》完整文本获取指南

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
