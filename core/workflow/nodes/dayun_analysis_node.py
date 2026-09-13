"""
大运分析节点
"""
from typing import Dict, Any
from .analysis_node import AnalysisNode
import json
import re


class DayunAnalysisNode(AnalysisNode):
    """大运分析节点"""
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行大运分析
        
        Args:
            input_data: 包含四柱、大运列表、当前大运、日主强弱的数据
        
        Returns:
            大运分析结果
        """
        # 1. 准备输入数据
        sizhu = input_data.get('sizhu', {})
        dayun_list = input_data.get('dayun_list', [])
        current_dayun = input_data.get('current_dayun', {})
        
        # 2. 获取日主强弱和五行喜忌
        day_strength = self._get_day_strength(input_data)
        wuxing_xi_ji = self._get_wuxing_xi_ji(input_data)
        
        # 3. 构建动态提示词
        prompt = self._build_dayun_prompt(
            sizhu,
            dayun_list,
            current_dayun,
            day_strength,
            wuxing_xi_ji
        )
        
        # 4. 调用LLM
        result = self._call_llm(prompt)
        
        # 5. 解析结果
        parsed_result = self._parse_result(result)
        
        return {
            "analysis_result": parsed_result,
            "current_dayun": current_dayun,
            "raw_response": result
        }
    
    def _get_day_strength(self, input_data: Dict) -> str:
        """获取日主强弱"""
        # 从十神分析结果中获取
        if 'shishen_analysis_result' in input_data:
            result = input_data['shishen_analysis_result']
            if 'day_strength' in result:
                return result['day_strength'].get('status', 'unknown')
        
        return 'unknown'
    
    def _get_wuxing_xi_ji(self, input_data: Dict) -> str:
        """获取五行喜忌"""
        # 从五行分析结果中获取
        if 'wuxing_analysis_result' in input_data:
            result = input_data['wuxing_analysis_result']
            if 'analysis_result' in result:
                content = result['analysis_result'].get('content', '')
                # 简单提取喜用五行和忌讳五行
                if '喜用五行' in content:
                    return content
        
        return '未提供'
    
    def _build_dayun_prompt(
        self,
        sizhu: Dict,
        dayun_list: list,
        current_dayun: Dict,
        day_strength: str,
        wuxing_xi_ji: str
    ) -> str:
        """构建大运分析提示词"""
        # 加载提示词模板
        template = self._load_prompt_template()
        
        # 构建四柱信息
        sizhu_info = self._format_sizhu(sizhu)
        
        # 构建大运列表
        dayun_info = self._format_dayun_list(dayun_list, current_dayun)
        
        # 构建当前大运
        current_info = self._format_current_dayun(current_dayun)
        
        # 替换模板中的变量
        prompt = template.replace('{sizhu}', sizhu_info)
        prompt = prompt.replace('{dayun_list}', dayun_info)
        prompt = prompt.replace('{current_dayun}', current_info)
        prompt = prompt.replace('{day_strength}', day_strength)
        prompt = prompt.replace('{wuxing_xi_ji}', wuxing_xi_ji)
        
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
    
    def _format_dayun_list(self, dayun_list: list, current_dayun: Dict) -> str:
        """格式化大运列表"""
        if not dayun_list:
            return "无大运数据"
        
        parts = []
        for i, dy in enumerate(dayun_list[:8]):  # 只显示前8步
            gan = dy.get('gan', '?')
            zhi = dy.get('zhi', '?')
            start_age = dy.get('start_age', '?')
            end_age = dy.get('end_age', '?')
            
            # 标注当前大运
            is_current = ""
            if current_dayun:
                if gan == current_dayun.get('gan') and zhi == current_dayun.get('zhi'):
                    is_current = " ← 当前大运"
            
            parts.append(f"第{i+1}步: {gan}{zhi} ({start_age}-{end_age}岁){is_current}")
        
        return "\n".join(parts)
    
    def _format_current_dayun(self, current_dayun: Dict) -> str:
        """格式化当前大运"""
        if not current_dayun:
            return "未提供当前大运信息"
        
        gan = current_dayun.get('gan', '?')
        zhi = current_dayun.get('zhi', '?')
        start_age = current_dayun.get('start_age', '?')
        end_age = current_dayun.get('end_age', '?')
        
        return f"{gan}{zhi} ({start_age}-{end_age}岁)"
    
    def _parse_result(self, result: str) -> Dict[str, Any]:
        """解析大运分析结果"""
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
