# 黄帝内经数据目录

## 目录说明

- `raw/`: 存放原始文本文件（TXT格式，UTF-8编码）
  - 应包含《素问》和《灵枢》两部分
  - 建议文件名：`suwen.txt` 和 `lingshu.txt`
  
- `structured/`: 存放结构化后的JSON数据
  - 由 `huangdi_text_processor.py` 自动生成
  
- `vector_db/`: 存放向量数据库文件
  - 由 `huangdi_vector_store.py` 自动生成

## 获取文本

您可以从以下来源获取《黄帝内经》完整文本：

1. 黄帝内经网：https://www.huangdineijing.com.cn/download/
2. 国学网、中国古籍网等
3. GitHub开源古籍项目

下载后，请将文本文件（UTF-8编码）放入 `raw/` 目录。

## 示例文本格式

文本应包含完整的《素问》和《灵枢》内容，建议格式：
- 每篇以篇名开头（如"第一篇 上古天真论"）
- 每章以章节名开头
- 原文和注释分开标注

