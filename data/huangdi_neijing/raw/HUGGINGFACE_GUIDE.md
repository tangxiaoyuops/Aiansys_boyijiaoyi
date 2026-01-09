# 从HuggingFace获取《黄帝内经》完整数据集

## HuggingFace搜索结果

经过搜索，HuggingFace上**没有专门的《黄帝内经》完整数据集**。

可能相关的数据集：
- `Chinese-Medical-Dialogues` - 中医对话数据集（不包含完整《黄帝内经》文本）

## 更可靠的获取方法

### 方法1: 中国哲学书电子化计划（推荐，最可靠）

**网站**: http://ctext.org

**直接链接**:
- 素问: http://ctext.org/huangdi-neijing/suwen
- 灵枢: http://ctext.org/huangdi-neijing/lingshu

**使用方法**:
1. 访问上述链接
2. 在页面上选择"显示原文"或"View Original"
3. 复制所有文本内容
4. 保存为UTF-8编码的TXT文件

**优点**:
- 最权威的古籍资源
- 文本完整准确
- 免费公开

### 方法2: 使用提供的脚本

运行脚本自动获取（可能不完整）:
```bash
python scripts/fetch_from_ctext.py
```

### 方法3: 手动搜索GitHub

在GitHub搜索:
- 关键词: `黄帝内经 txt` 或 `huangdi neijing`
- 可能找到的开源项目会包含完整文本

### 方法4: 古籍网站下载

- 中国古籍网: https://www.guoxue.com/
- 国学资源网: https://www.guoxueziyuan.com/
- 古籍在线: https://www.guji.cn/

## 如果使用HuggingFace datasets库

如果将来HuggingFace上有相关数据集，可以使用:

```python
from datasets import load_dataset

# 加载数据集
dataset = load_dataset('数据集ID')

# 处理数据
for split in dataset.keys():
    data = dataset[split]
    # 保存为文本文件
    with open('output.txt', 'w', encoding='utf-8') as f:
        for item in data:
            f.write(item['text'] + '\n\n')
```

## 当前状态

系统已使用部分内容（37个章节）初始化了知识库，可以正常使用。

如需更完整的内容，建议从 **ctext.org** 手动获取完整文本。

