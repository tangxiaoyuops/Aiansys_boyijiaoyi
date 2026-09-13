"""
批量替换server/app.py中的json.dumps为safe_json_dumps
"""
import re

# 读取文件
with open('server/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 统计原始数量
original_count = len(re.findall(r'json\.dumps\([^)]+ensure_ascii=False[^)]*\)', content))
print(f"找到 {original_count} 处需要替换的 json.dumps")

# 替换模式
# 模式1: json.dumps({...}, ensure_ascii=False) -> safe_json_dumps({...})
# 模式2: json.dumps({...}, ensure_ascii=False, ...) -> safe_json_dumps({...}, ...)

# 第一步：移除 ensure_ascii=False 参数
content = re.sub(
    r'json\.dumps\(([^)]+),\s*ensure_ascii=False\s*\)',
    r'json.dumps(\1)',
    content
)

# 第二步：移除 ensure_ascii=False, ... 的情况
content = re.sub(
    r'json\.dumps\(([^)]+),\s*ensure_ascii=False,\s*([^)]+)\)',
    r'json.dumps(\1, \2)',
    content
)

# 第三步：移除 ..., ensure_ascii=False 的情况
content = re.sub(
    r'json\.dumps\(([^)]+),\s*([^)]+),\s*ensure_ascii=False\s*\)',
    r'json.dumps(\1, \2)',
    content
)

# 第四步：将剩余的 json.dumps 替换为 safe_json_dumps（排除已经是在safe_json_dumps函数定义中的）
content = re.sub(
    r'(?<!def )(?<!cls=CustomJSONEncoder, )json\.dumps\(',
    r'safe_json_dumps(',
    content
)

# 统计替换后数量
new_count = len(re.findall(r'safe_json_dumps\(', content))
remaining_json_dumps = len(re.findall(r'(?<!def safe_)json\.dumps\(', content))

print(f"替换完成：{new_count} 处使用了 safe_json_dumps")
print(f"剩余 {remaining_json_dumps} 处使用 json.dumps")

# 写回文件
with open('server/app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("文件已更新")
