"""
十神分析节点
"""
from typing import Dict, Any
from .analysis_node import AnalysisNode
import json
import re


class ShishenAnalysisNode(AnalysisNode):
    """十神分析节点"""
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行十神分析
        
        Args:
            input_data: 包含四柱、十神配置、日主强弱的数据
        
        Returns:
            十神分析结果
        """
        # 1. 准备输入数据
        sizhu = input_data.get('sizhu', {})
        shishen_data = input_data.get('shishen_data', {})
        
        # 2. 判断日主强弱(需要先调用五行分析)
        day_strength = self._determine_day_strength(sizhu, input_data)
        
        # 3. 构建动态提示词
        prompt = self._build_shishen_prompt(sizhu, shishen_data, day_strength)
        
        # 4. 调用LLM
        result = self._call_llm(prompt)
        
        # 5. 解析结果
        parsed_result = self._parse_result(result)
        
        return {
            "analysis_result": parsed_result,
            "day_strength": day_strength,
            "raw_response": result
        }
    
    def _determine_day_strength(self, sizhu: Dict, input_data: Dict) -> Dict[str, Any]:
        """
        判断日主强弱
        
        Args:
            sizhu: 四柱数据
            input_data: 输入数据
        
        Returns:
            日主强弱判断结果
        """
        # 如果前面已经有五行分析结果,直接使用
        if 'wuxing_analysis_result' in input_data:
            wuxing_result = input_data['wuxing_analysis_result']
            if 'analysis_result' in wuxing_result:
                content = wuxing_result['analysis_result'].get('content', '')
                # 简单判断是否包含"身强"或"身弱"
                if '身强' in content or '身旺' in content:
                    return {"status": "身强", "confidence": 0.9}
                elif '身弱' in content:
                    return {"status": "身弱", "confidence": 0.9}
        
        # 否则需要自己判断
        # TODO: 调用五行分析判断日主强弱
        # 这里简化处理,实际应该调用五行分析节点
        return {"status": "unknown", "confidence": 0.5}
    
    def _build_shishen_prompt(
        self,
        sizhu: Dict,
        shishen_data: Dict,
        day_strength: Dict
    ) -> str:
        """构建十神分析提示词"""
        # 加载提示词模板
        template = self._load_prompt_template()
        
        # 构建四柱信息
        sizhu_info = self._format_sizhu(sizhu)
        
        # 构建十神信息
        shishen_info = self._format_shishen(shishen_data)
        
        # 替换模板中的变量
        prompt = template.replace('{sizhu}', sizhu_info)
        prompt = prompt.replace('{shishen_data}', shishen_info)
        prompt = prompt.replace('{day_strength}', day_strength.get('status', 'unknown'))
        
        return prompt
    
    def _format_sizhu(self, sizhu: Dict) -> str:
        """格式化四柱信息"""
        parts = []
        zhu_names = {
            'nian_zhu': '年柱',
            'yue_zhu': '月柱',
            'ri_zhu': '日柱',
            'shi_zhu': '时柱'
        }
        
        for key, name in zhu_names.items():
            zhu = sizhu.get(key, {})
            if zhu:
                gan = zhu.get('tian_gan', '?')
                zhi = zhu.get('di_zhi', '?')
                parts.append(f"{name}: {gan}{zhi}")
        
        return "\n".join(parts)
    
    def _format_shishen(self, shishen_data: Dict) -> str:
        """格式化十神信息"""
        parts = []
        zhu_names = {
            'nian_zhu': '年柱',
            'yue_zhu': '月柱',
            'ri_zhu': '日柱',
            'shi_zhu': '时柱'
        }
        
        for key, name in zhu_names.items():
            zhu_data = shishen_data.get(key, {})
            if zhu_data:
                gan_shishen = zhu_data.get('gan_shishen', '')
                zhi_shishen = zhu_data.get('zhi_shishen', '')
                parts.append(f"{name}: 天干{gan_shishen}, 地支{zhi_shishen}")
        
        return "\n".join(parts)
    
    def _parse_result(self, result: str) -> Dict[str, Any]:
        """解析十神分析结果"""
        try:
            # 尝试提取JSON
            json_match = re.search(r'\{[^}]+\}', result, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                return {
                    "content": result,
                    "structured_data": parsed,
                    "length": len(result)
                }
        except Exception:
            pass
        
        # 如果解析失败,返回原始内容
        return {
            "content": result,
            "structured_data": {},
            "length": len(result)
        }
