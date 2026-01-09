# 黄帝内经模块使用说明

## 一、初始化知识库

在使用黄帝内经模块之前，需要先初始化知识库：

```bash
python core/tools/init_huangdi_kb.py
```

这个脚本会：
1. 处理原始文本文件（`raw/suwen.txt` 和 `raw/lingshu.txt`）
2. 生成结构化数据（保存到 `structured/` 目录）
3. 构建向量数据库（保存到 `vector_db/` 目录）

## 二、准备文本文件

将《黄帝内经》的完整文本文件放入 `raw/` 目录：
- `suwen.txt` - 素问部分
- `lingshu.txt` - 灵枢部分

如果只有示例文件（`suwen_sample.txt` 和 `lingshu_sample.txt`），系统会自动使用它们。

## 三、API使用

### 3.1 知识查询

查询《黄帝内经》中的理论知识：

```python
POST /api/huangdi/analyze
{
    "question": "什么是阴阳",
    "query_type": "query",  # 可选，自动检测
    "include_llm": true
}
```

### 3.2 诊断建议

根据症状提供理论分析（仅提供理论参考）：

```python
POST /api/huangdi/analyze
{
    "question": "头痛、发热、恶寒",
    "query_type": "diagnosis",
    "include_llm": true
}
```

### 3.3 健康咨询

基于内经理论提供养生建议：

```python
POST /api/huangdi/analyze
{
    "question": "平时容易疲劳，手脚比较凉",
    "query_type": "consultation",
    "include_llm": true,
    "context": {
        "season": "冬",
        "age": 35
    }
}
```

## 四、Python代码使用

### 4.1 知识查询

```python
from core.agents.huangdi_query_agent import huangdi_query_node

result = huangdi_query_node("什么是阴阳", include_llm=True)
print(result['llm_explanation'])
```

### 4.2 诊断建议

```python
from core.agents.huangdi_diagnosis_agent import huangdi_diagnosis_node

result = huangdi_diagnosis_node("头痛、发热、恶寒", include_llm=True)
print(result['llm_analysis'])
```

### 4.3 健康咨询

```python
from core.agents.huangdi_consultation_agent import huangdi_consultation_node

result = huangdi_consultation_node(
    "平时容易疲劳，手脚比较凉",
    season="冬",
    age=35,
    include_llm=True
)
print(result['llm_suggestions'])
```

### 4.4 完整分析（自动路由）

```python
from core.agents.huangdi_analysis_agent import huangdi_complete_analysis

# 自动检测查询类型
result = huangdi_complete_analysis("什么是阴阳", include_llm=True)

# 或指定查询类型
result = huangdi_complete_analysis(
    "头痛、发热、恶寒",
    query_type="diagnosis",
    include_llm=True
)
```

## 五、注意事项

1. **免责声明**：所有诊断建议和健康咨询仅提供理论参考，不能替代专业医疗诊断。如有疾病，请及时就医。

2. **数据准确性**：确保使用权威版本的《黄帝内经》文本。

3. **首次使用**：首次使用前需要运行初始化脚本构建知识库。

4. **向量数据库**：向量数据库构建可能需要一些时间，请耐心等待。

5. **LLM配置**：需要配置OpenAI API密钥（或使用本地embedding模型）。

## 六、目录结构

```
data/huangdi_neijing/
├── raw/                    # 原始文本文件
│   ├── suwen.txt          # 素问（完整版）
│   ├── lingshu.txt        # 灵枢（完整版）
│   ├── suwen_sample.txt   # 素问示例
│   └── lingshu_sample.txt # 灵枢示例
├── structured/             # 结构化数据（自动生成）
│   ├── chapters.json      # 章节数据
│   └── index.json         # 索引数据
└── vector_db/              # 向量数据库（自动生成）
    └── chroma_db/         # ChromaDB数据文件
```

## 七、故障排除

### 7.1 向量数据库初始化失败

如果遇到embedding初始化失败，可以：
1. 检查OpenAI API配置
2. 或使用本地embedding模型（sentence-transformers）

### 7.2 文本处理失败

确保文本文件：
1. 使用UTF-8编码
2. 包含完整的《素问》和《灵枢》内容
3. 格式规范（每篇以"第X篇 篇名"开头）

### 7.3 搜索无结果

如果搜索无结果，可能是：
1. 知识库未初始化（运行初始化脚本）
2. 查询文本与经文内容差异较大（尝试使用更通用的关键词）

