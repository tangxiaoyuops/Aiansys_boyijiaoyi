"""
流年分析节点
"""
from typing import Dict, Any
from .analysis_node import AnalysisNode
import json
import re


class LiunianAnalysisNode(AnalysisNode):
    """流年分析节点"""
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行流年分析
        
        Args:
            input_data: 包含四柱、大运数据、流年数据、日主强弱的数据
        
        Returns:
            流年分析结果
        """
        # 1. 准备输入数据
        sizhu = input_data.get('sizhu', {})
        dayun_data = input_data.get('dayun_data', {})
        liunian_data = input_data.get('liunian_data', {})
        
        # 2. 获取日主强弱和五行喜忌
        day_strength = self._get_day_strength(input_data)
        wuxing_xi_ji = self._get_wuxing_xi_ji(input_data)
        
        # 3. 构建动态提示词
        prompt = self._build_liunian_prompt(
            sizhu,
            dayun_data,
            liunian_data,
            day_strength,
            wuxing_xi_ji
        )
        
        # 4. 调用LLM
        result = self._call_llm(prompt)
        
        # 5. 解析结果
        parsed_result = self._parse_result(result)
        
        return {
            "analysis_result": parsed_result,
            "liunian_data": liunian_data,
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
                if '喜用五行' in content:
                    return content
        
        return '未提供'
    
    def _build_liunian_prompt(
        self,
        sizhu: Dict,
        dayun_data: Dict,
        liunian_data: Dict,
        day_strength: str,
        wuxing_xi_ji: str
    ) -> str:
        """构建流年分析提示词"""
        # 加载提示词模板
        template = self._load_prompt_template()
        
        # 构建四柱信息
        sizhu_info = self._format_sizhu(sizhu)
        
        # 构建大运数据
        dayun_info = self._format_dayun_data(dayun_data)
        
        # 构建流年数据
        liunian_info = self._format_liunian_data(liunian_data)
        
        # 替换模板中的变量
        prompt = template.replace('{sizhu}', sizhu_info)
        prompt = prompt.replace('{dayun_data}', dayun_info)
        prompt = prompt.replace('{liunian_data}', liunian_info)
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
    
    def _format_dayun_data(self, dayun_data: Dict) -> str:
        """格式化大运数据"""
        if not dayun_data:
            return "无大运数据"
        
        # 如果是从大运分析节点传来的结果
        if 'analysis_result' in dayun_data:
            content = dayun_data['analysis_result'].get('content', '')
            return content[:500]  # 限制长度
        
        return str(dayun_data)
    
    def _format_liunian_data(self, liunian_data: Dict) -> str:
        """格式化流年数据"""
        if not liunian_data:
            return "无流年数据"
        
        parts = []
        # 显示当前流年和未来几年
        from datetime import datetime
        current_year = datetime.now().year
        
        for year in range(current_year - 1, current_year + 3):
            year_str = str(year)
            if year_str in liunian_data:
                liunian = liunian_data[year_str]
                gan = liunian.get('gan', '')
                zhi = liunian.get('zhi', '')
                gan_zhi = liunian.get('gan_zhi', f"{gan}{zhi}")
                is_current = " ← 当前流年" if year == current_year else ""
                parts.append(f"{year}年: {gan_zhi}{is_current}")
        
        return "\n".join(parts)
    
    def _parse_result(self, result: str) -> Dict[str, Any]:
        """解析流年分析结果"""
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
