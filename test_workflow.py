"""
测试八字分析工作流系统
"""
import sys
sys.path.insert(0, 'g:/projects/博弈交易/Aiansys_boyijiaoyi')

from core.workflow.engine import WorkflowEngine
from core.tools.bazi_calculator import calculate_sizhu

def test_workflow():
    """测试工作流"""
    print("=" * 80)
    print("八字分析工作流系统测试")
    print("=" * 80)
    
    # 1. 初始化工作流引擎
    engine = WorkflowEngine(max_workers=3)
    print("[OK] 工作流引擎初始化成功")
    
    # 2. 创建测试数据
    print("\n准备测试数据...")
    birth_year = 1985
    birth_month = 7
    birth_day = 15
    birth_hour = 14
    gender = '女'
    
    # 计算四柱
    sizhu = calculate_sizhu(birth_year, birth_month, birth_day, birth_hour)
    
    user_question = "请帮我全面分析一下我的八字命局"
    
    input_data = {
        "user_question": user_question,
        "conversation_history": [],
        "sizhu": sizhu,
        "birth_info": {
            "year": birth_year,
            "month": birth_month,
            "day": birth_day,
            "hour": birth_hour,
            "gender": gender
        }
    }
    
    print(f"[OK] 测试数据准备完成")
    print(f"  用户问题: {user_question}")
    print(f"  出生时间: {birth_year}年{birth_month}月{birth_day}日{birth_hour}时")
    print(f"  四柱: {sizhu['nian_zhu']['tian_gan']}{sizhu['nian_zhu']['di_zhi']}年 "
          f"{sizhu['yue_zhu']['tian_gan']}{sizhu['yue_zhu']['di_zhi']}月 "
          f"{sizhu['ri_zhu']['tian_gan']}{sizhu['ri_zhu']['di_zhi']}日 "
          f"{sizhu['shi_zhu']['tian_gan']}{sizhu['shi_zhu']['di_zhi']}时")
    
    # 3. 创建简化工作流
    print("\n创建工作流...")
    workflow_config = {
        "name": "test_workflow",
        "description": "测试工作流",
        "steps": [
            {
                "id": "intent_recognition",
                "type": "intent_node",
                "config": {
                    "model": "gpt-4o",
                    "timeout": 10
                }
            }
        ]
    }
    
    from core.workflow.engine import Workflow
    workflow = Workflow(workflow_config)
    print(f"[OK] 工作流创建成功: {workflow.name}")
    
    # 4. 执行工作流
    print("\n开始执行工作流...")
    results = engine.execute_workflow(workflow, input_data)
    
    # 5. 显示结果
    print("\n" + "=" * 80)
    print("执行结果")
    print("=" * 80)
    
    for step_id, result in results.items():
        print(f"\n节点: {step_id}")
        print(f"状态: {result.get('status')}")
        print(f"耗时: {result.get('elapsed_time', 0):.2f}秒")
        
        if result.get('status') == 'success':
            if 'intent' in result:
                print(f"识别意图: {result['intent']}")
                print(f"置信度: {result['confidence']}")
                print(f"理由: {result['reason']}")
        else:
            print(f"错误: {result.get('error')}")
    
    print("\n" + "=" * 80)
    print("测试完成！")
    print("=" * 80)

if __name__ == "__main__":
    test_workflow()
