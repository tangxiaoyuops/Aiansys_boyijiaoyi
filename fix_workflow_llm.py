"""
快速修复工作流节点的LLM调用
使用统一的LLM客户端和正确的模型配置
"""
import os
import re

# 需要修复的文件
files_to_fix = [
    'core/workflow/nodes/intent_node.py',
    'core/workflow/nodes/analysis_node.py',
    'core/workflow/nodes/wuxing_analysis_node.py',
    'core/workflow/nodes/integration_node.py',
    'core/workflow/nodes/dialogue_node.py',
    'core/workflow/nodes/shishen_analysis_node.py',
    'core/workflow/nodes/dayun_analysis_node.py',
    'core/workflow/nodes/liunian_analysis_node.py',
]

def fix_call_llm_method(file_path):
    """修复_call_llm方法,使用统一的LLM客户端"""
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经有正确的导入
    if 'from core.tools.llm_client import call_llm' not in content:
        # 添加导入
        content = content.replace(
            'from typing import Dict, Any',
            'from typing import Dict, Any\nfrom core.tools.llm_client import call_llm'
        )
    
    # 替换_call_llm方法
    # 查找旧的_call_llm方法
    pattern = r'def _call_llm\(self, prompt: str\) -> str:.*?return response\.choices\[0\]\.message\.content'
    
    new_method = '''def _call_llm(self, prompt: str) -> str:
        """调用LLM"""
        # 使用统一的LLM客户端
        from core.tools.llm_client import call_llm
        
        result = call_llm(
            system_prompt="你是一位专业的八字分析专家。",
            user_prompt=prompt,
            model=self.model,
            temperature=0.7,
            timeout=self.timeout
        )
        
        return result'''
    
    # 执行替换
    content_new = re.sub(pattern, new_method, content, flags=re.DOTALL)
    
    if content_new != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content_new)
        print(f"✅ 已修复: {file_path}")
    else:
        print(f"⏭️  无需修改: {file_path}")

# 执行修复
print("开始修复工作流节点的LLM调用...")
print("=" * 80)

for file_path in files_to_fix:
    full_path = os.path.join('G:/projects/博弈交易/Aiansys_boyijiaoyi', file_path)
    fix_call_llm_method(full_path)

print("=" * 80)
print("修复完成!")
