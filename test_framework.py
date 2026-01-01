"""
测试框架脚本
验证LangGraph工作流是否正确搭建
"""
import sys

def test_imports():
    """测试导入"""
    print("测试导入...")
    try:
        from core.models.state import AnalysisState
        print("✓ 状态模型导入成功")
        
        from core.tools.data_fetcher import fetch_stock_data
        print("✓ 数据获取工具导入成功")
        
        from core.agents.intent_agent import intent_recognition_node
        print("✓ 意图识别Agent导入成功")
        
        from core.graph.analysis_graph import compiled_graph
        print("✓ LangGraph工作流导入成功")
        
        print("\n所有核心模块导入成功！")
        return True
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_graph_structure():
    """测试图结构"""
    print("\n测试图结构...")
    try:
        from core.graph.analysis_graph import analysis_graph
        
        # 检查节点
        nodes = analysis_graph.nodes
        print(f"✓ 图节点数量: {len(nodes)}")
        print(f"  节点列表: {list(nodes.keys())}")
        
        # 检查边
        edges = analysis_graph.edges
        print(f"✓ 图边数量: {len(edges)}")
        
        print("\n图结构验证成功！")
        return True
    except Exception as e:
        print(f"✗ 图结构验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("博弈交易法分析系统 - 框架测试")
    print("=" * 50)
    
    # 测试导入
    if not test_imports():
        sys.exit(1)
    
    # 测试图结构
    if not test_graph_structure():
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✓ 所有测试通过！框架搭建成功！")
    print("=" * 50)
    print("\n下一步：")
    print("1. 安装依赖: pip install -r requirements.txt")
    print("2. 启动服务: python -m uvicorn server.app:app --host 0.0.0.0 --port 8000")
    print("3. 测试API: curl http://localhost:8000/")


