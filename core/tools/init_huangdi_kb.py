"""
初始化黄帝内经知识库
处理文本文件，构建结构化数据和向量数据库
"""
import logging
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("开始初始化黄帝内经知识库")
    logger.info("=" * 60)
    
    try:
        # 1. 处理文本文件，生成结构化数据
        logger.info("\n步骤1: 处理文本文件，生成结构化数据...")
        from core.tools.huangdi_text_processor import process_all_files
        text_result = process_all_files()
        
        if not text_result.get('success'):
            logger.error("文本处理失败")
            return False
        
        logger.info(f"✓ 文本处理完成，共 {text_result.get('total_chapters', 0)} 个章节")
        
        # 2. 构建向量数据库
        logger.info("\n步骤2: 构建向量数据库...")
        from core.tools.huangdi_vector_store import build_vector_store
        vector_result = build_vector_store()
        
        if not vector_result.get('success'):
            logger.error("向量数据库构建失败")
            return False
        
        logger.info(f"✓ 向量数据库构建完成，共 {vector_result.get('total_chunks', 0)} 个文档块")
        
        # 3. 测试知识库
        logger.info("\n步骤3: 测试知识库...")
        from core.tools.huangdi_knowledge_base import get_knowledge_base
        kb = get_knowledge_base()
        
        # 测试搜索
        test_query = "什么是阴阳"
        results = kb.search(test_query, search_type="hybrid", k=3)
        logger.info(f"✓ 测试搜索成功，找到 {len(results.get('combined_results', []))} 条结果")
        
        # 获取统计信息
        stats = kb.get_statistics()
        logger.info(f"\n知识库统计信息:")
        logger.info(f"  总章节数: {stats['total_chapters']}")
        logger.info(f"  素问: {stats['suwen_count']} 篇")
        logger.info(f"  灵枢: {stats['lingshu_count']} 篇")
        logger.info(f"  主题数: {len(stats['themes'])}")
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ 黄帝内经知识库初始化完成！")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"初始化失败: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

