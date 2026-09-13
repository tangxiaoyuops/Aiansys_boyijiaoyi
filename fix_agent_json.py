"""
修复Agent框架的JSON序列化问题
"""
import re

file_path = 'core/agent_framework/api/app_stream.py'

# 读取文件
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 替换所有 json.dumps(..., ensure_ascii=False) 为 safe_json_dumps(...)
content = re.sub(
    r'json\.dumps\(([^)]+),\s*ensure_ascii=False\s*\)',
    r'safe_json_dumps(\1)',
    content
)

# 替换 json.dumps(..., ensure_ascii=False, ...) 为 safe_json_dumps(..., ...)
content = re.sub(
    r'json\.dumps\(([^)]+),\s*ensure_ascii=False,\s*([^)]+)\)',
    r'safe_json_dumps(\1, \2)',
    content
)

# 写回文件
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("修复完成！")

# 验证
with open(file_path, 'r', encoding='utf-8') as f:
    new_content = f.read()
    
json_dumps_count = len(re.findall(r'json\.dumps', new_content))
safe_dumps_count = len(re.findall(r'safe_json_dumps', new_content))

print(f"剩余 json.dumps: {json_dumps_count}")
print(f"使用 safe_json_dumps: {safe_dumps_count}")
