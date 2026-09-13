"""
五行分析节点 - 真正集成Agent
"""
from typing import Dict, Any
from .base_node import BaseNode
from core.agents.bazi_config_agent import BaziConfigAgent
from core.agents.bazi_analysis_logic_agent import BaziAnalysisAgent
import os


class WuxingAnalysisNode(BaseNode):
    """五行分析节点 - 集成Agent"""
    
    def __init__(self, node_id: str, config: Dict[str, Any]):
        super().__init__(node_id, config)
        self.config_agent = BaziConfigAgent()
        self.analysis_agent = BaziAnalysisAgent()
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行五行分析
        
        Args:
            input_data: 包含四柱、五行数据等
        
        Returns:
            五行分析结果
        """
        # 1. 提取输入数据
        sizhu = input_data.get('sizhu', {})
        wuxing_data = input_data.get('wuxing_analysis', {})
        dayun_data = input_data.get('dayun_analysis', {})
        
        # 2. 使用AnalysisAgent分析场景
        context = self.analysis_agent.analyze_situation(
            sizhu,
            wuxing_data,
            {},  # shishen
            dayun_data,
            {}   # liunian
        )
        
        # 3. 构建动态提示词
        dynamic_prompt = self._build_wuxing_prompt(sizhu, wuxing_data, context)
        
        # 4. 调用LLM
        result = self._call_llm(dynamic_prompt)
        
        return {
            "analysis_type": "wuxing",
            "day_strength": context.get('day_strength', 'unknown'),
            "content": result,
            "context": context
        }
    
    def _build_wuxing_prompt(
        self,
        sizhu: Dict[str, Any],
        wuxing_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """构建五行分析提示词"""
        
        # 使用ConfigAgent获取第一步配置
        step1_config = self.config_agent.get_analysis_step_config("step1")
        
        # 获取快速参考
        day_strength = context.get('day_strength', 'unknown')
        if day_strength == 'strong':
            quick_ref = self.analysis_agent.get_quick_reference("身强格十神")
        else:
            quick_ref = self.analysis_agent.get_quick_reference("身弱格十神")
        
        prompt = f"""你是精通"子平真诠"与"滴天髓"的实战派命理师，现在需要进行五行分析。

{step1_config}

## 快速参考
{quick_ref}

## 命局数据

### 四柱
"""
        
        # 添加四柱信息
        if sizhu:
            for zhu_name, zhu_key in [('年柱', 'nian_zhu'), ('月柱', 'yue_zhu'), 
                                       ('日柱', 'ri_zhu'), ('时柱', 'shi_zhu')]:
                zhu = sizhu.get(zhu_key, {})
                if zhu:
                    gan = zhu.get('tian_gan', '')
                    zhi = zhu.get('di_zhi', '')
                    cang_gan = zhu.get('cang_gan', [])
                    cang_gan_str = f"（藏干: {'、'.join(cang_gan)}）" if cang_gan else ""
                    prompt += f"{zhu_name}: {gan}{zhi}{cang_gan_str}\n"
        
        # 添加五行信息
        prompt += f"\n### 五行分布\n"
        if wuxing_data:
            wuxing_count = wuxing_data.get('wuxing_data', {}).get('wuxing_count', {})
            if wuxing_count:
                prompt += f"金: {wuxing_count.get('金', 0)}, "
                prompt += f"木: {wuxing_count.get('木', 0)}, "
                prompt += f"水: {wuxing_count.get('水', 0)}, "
                prompt += f"火: {wuxing_count.get('火', 0)}, "
                prompt += f"土: {wuxing_count.get('土', 0)}\n"
        
        # 添加分析要求
        prompt += f"""

## 分析要求

1. **判断日主强弱**：根据地支根气、天干生扶判断
2. **分析五行旺衰**：各五行的强弱分布
3. **判断五行流通**：流通还是阻塞
4. **给出补救建议**：如何平衡五行

## 输出格式

**日主强弱**：[身强/身弱]

**五行旺衰**：
- 金：[旺/相/休/囚/死]
- 木：[旺/相/休/囚/死]
...

**五行流通**：
[描述五行生克流通情况]

**补救建议**：
[具体建议]
"""
        
        return prompt
    
    def _call_llm(self, prompt: str) -> str:
        """调用LLM"""
        from core.tools.llm_client import call_llm
        
        result = call_llm(
            system_prompt="你是一位精通'子平真诠'与'滴天髓'的实战派命理师。",
            user_prompt=prompt,
            model=self.model,
            temperature=0.7,
            timeout=self.timeout
        )
        
        return result
