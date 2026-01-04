"""
紫微斗数模块测试
测试各个计算模块和Agent的功能
"""
import unittest
from datetime import datetime

from core.tools.ziwei_calculator import (
    create_pan,
    get_tian_gan,
    get_di_zhi,
    calculate_ming_gong,
    calculate_shen_gong,
    calculate_ziwei_star,
)
from core.tools.ziwei_si_hua import get_si_hua_stars, apply_si_hua_to_pan
from core.tools.ziwei_daxian import determine_daxian_direction, get_current_daxian
from core.tools.ziwei_liunian import get_current_liunian
from core.tools.ziwei_liuyue import get_current_liuyue
from core.tools.ziwei_shensha import calculate_all_shensha
from core.tools.ziwei_geju import check_classic_geju
from core.agents.ziwei_pan_agent import ziwei_pan_node
from core.agents.ziwei_analysis_agent import ziwei_complete_analysis


class TestZiweiCalculator(unittest.TestCase):
    """测试排盘计算器"""
    
    def test_tian_gan_di_zhi(self):
        """测试天干地支计算"""
        # 测试1984年（甲子年）
        self.assertEqual(get_tian_gan(1984), '甲')
        self.assertEqual(get_di_zhi(1984), '子')
        
        # 测试2024年
        self.assertEqual(get_tian_gan(2024), '甲')
        self.assertEqual(get_di_zhi(2024), '辰')
    
    def test_ming_shen_gong(self):
        """测试命宫身宫计算"""
        # 测试农历正月寅时
        ming_gong = calculate_ming_gong(1, '寅')
        shen_gong = calculate_shen_gong(1, '寅')
        
        self.assertIsInstance(ming_gong, int)
        self.assertIsInstance(shen_gong, int)
        self.assertGreaterEqual(ming_gong, 0)
        self.assertLess(ming_gong, 12)
        self.assertGreaterEqual(shen_gong, 0)
        self.assertLess(shen_gong, 12)
    
    def test_ziwei_star(self):
        """测试紫微星位置计算"""
        # 测试农历正月子时
        ziwei_palace = calculate_ziwei_star(1, '子')
        
        self.assertIsInstance(ziwei_palace, int)
        self.assertGreaterEqual(ziwei_palace, 0)
        self.assertLess(ziwei_palace, 12)
    
    def test_create_pan(self):
        """测试创建命盘"""
        # 测试一个具体的日期
        pan_data = create_pan(1990, 1, 1, 12, '男')
        
        self.assertIn('birth_info', pan_data)
        self.assertIn('ming_gong', pan_data)
        self.assertIn('shen_gong', pan_data)
        self.assertIn('palaces', pan_data)
        self.assertEqual(len(pan_data['palaces']), 12)
        
        # 验证命宫
        ming_gong = pan_data['ming_gong']
        self.assertGreaterEqual(ming_gong, 0)
        self.assertLess(ming_gong, 12)
        
        # 验证每个宫位都有必要字段
        for palace in pan_data['palaces']:
            self.assertIn('index', palace)
            self.assertIn('name', palace)
            self.assertIn('main_stars', palace)
            self.assertIn('auxiliary_stars', palace)


class TestZiweiSiHua(unittest.TestCase):
    """测试四化星计算"""
    
    def test_get_si_hua_stars(self):
        """测试获取四化星配置"""
        # 测试甲年
        si_hua = get_si_hua_stars('甲')
        
        self.assertIn('化禄', si_hua)
        self.assertIn('化权', si_hua)
        self.assertIn('化科', si_hua)
        self.assertIn('化忌', si_hua)
        self.assertEqual(si_hua['化禄'], '廉贞')
    
    def test_apply_si_hua_to_pan(self):
        """测试四化星应用到命盘"""
        pan_data = create_pan(1990, 1, 1, 12, '男')
        year_gan = pan_data['birth_info']['year_gan']
        
        pan_data = apply_si_hua_to_pan(pan_data, year_gan)
        
        self.assertIn('si_hua', pan_data)
        self.assertIn('config', pan_data['si_hua'])
        self.assertIn('data', pan_data['si_hua'])


class TestZiweiDaxian(unittest.TestCase):
    """测试大限计算"""
    
    def test_determine_daxian_direction(self):
        """测试大限方向判断"""
        # 阳男应该顺行
        direction = determine_daxian_direction('甲', '男')
        self.assertEqual(direction, '顺')
        
        # 阴女应该顺行
        direction = determine_daxian_direction('乙', '女')
        self.assertEqual(direction, '顺')
    
    def test_get_current_daxian(self):
        """测试获取当前大限"""
        pan_data = create_pan(1990, 1, 1, 12, '男')
        birth_year = pan_data['birth_info']['year']
        current_year = 2024
        ming_gong = pan_data['ming_gong']
        year_gan = pan_data['birth_info']['year_gan']
        gender = pan_data['birth_info']['gender']
        
        direction = determine_daxian_direction(year_gan, gender)
        current_daxian = get_current_daxian(birth_year, current_year, ming_gong, direction)
        
        self.assertIn('number', current_daxian)
        self.assertIn('palace', current_daxian)
        self.assertIn('start_age', current_daxian)
        self.assertIn('end_age', current_daxian)


class TestZiweiLiunian(unittest.TestCase):
    """测试流年计算"""
    
    def test_get_current_liunian(self):
        """测试获取当前流年"""
        current_year = 2024
        liunian = get_current_liunian(current_year)
        
        self.assertIn('year', liunian)
        self.assertIn('gan', liunian)
        self.assertIn('zhi', liunian)
        self.assertIn('gan_zhi', liunian)
        self.assertEqual(liunian['year'], current_year)


class TestZiweiLiuyue(unittest.TestCase):
    """测试流月计算"""
    
    def test_get_current_liuyue(self):
        """测试获取当前流月"""
        from core.tools.ziwei_liunian import get_tian_gan
        
        current_year = 2024
        current_month = 1
        liunian_gan = get_tian_gan(current_year)
        
        liuyue = get_current_liuyue(liunian_gan, current_month)
        
        self.assertIn('month', liuyue)
        self.assertIn('gan', liuyue)
        self.assertIn('zhi', liuyue)
        self.assertIn('gan_zhi', liuyue)


class TestZiweiShensha(unittest.TestCase):
    """测试神煞计算"""
    
    def test_calculate_all_shensha(self):
        """测试计算所有神煞"""
        shensha = calculate_all_shensha('甲', '子', '甲')
        
        self.assertIsInstance(shensha, dict)
        # 应该至少包含红鸾天喜和孤辰寡宿
        self.assertIn('红鸾', shensha)
        self.assertIn('天喜', shensha)


class TestZiweiGeju(unittest.TestCase):
    """测试格局分析"""
    
    def test_check_classic_geju(self):
        """测试经典格局检测"""
        pan_data = create_pan(1990, 1, 1, 12, '男')
        
        detected_geju = check_classic_geju(pan_data)
        
        self.assertIsInstance(detected_geju, dict)


class TestZiweiAgents(unittest.TestCase):
    """测试Agent集成"""
    
    def test_ziwei_pan_node(self):
        """测试排盘Agent"""
        result = ziwei_pan_node(1990, 1, 1, 12, '男')
        
        self.assertTrue(result.get('success', False))
        self.assertIn('pan_data', result)
        self.assertIn('si_hua_analysis', result)
    
    def test_ziwei_complete_analysis(self):
        """测试完整分析Agent"""
        result = ziwei_complete_analysis(
            year=1990,
            month=1,
            day=1,
            hour=12,
            gender='男',
            include_daxian=True,
            include_shensha=True,
            include_geju=True,
            include_llm=False,  # 不测试LLM，避免API调用
        )
        
        self.assertTrue(result.get('success', False))
        self.assertIn('pan_data', result)
        self.assertIn('si_hua_analysis', result)
        if result.get('daxian_analysis'):
            self.assertIn('current_daxian', result['daxian_analysis'])


if __name__ == '__main__':
    unittest.main()


