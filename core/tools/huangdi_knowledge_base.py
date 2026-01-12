"""
黄帝内经知识库管理工具
统一管理结构化数据和向量数据，提供统一的查询接口
"""
import logging
from typing import List, Dict, Any, Optional

from core.tools.huangdi_text_processor import (
    load_structured_data,
    search_by_keyword as text_search_by_keyword,
    search_by_theme as text_search_by_theme,
)
from core.tools.huangdi_vector_store import (
    similarity_search,
    search_by_book,
    search_by_theme as vector_search_by_theme,
    build_vector_store,
    get_vector_store,
)

logger = logging.getLogger(__name__)


class HuangdiKnowledgeBase:
    """黄帝内经知识库"""
    
    def __init__(self):
        """初始化知识库"""
        self._structured_data = None
        self._vector_store_initialized = False
    
    def ensure_initialized(self):
        """确保知识库已初始化"""
        if self._structured_data is None:
            self._structured_data = load_structured_data()
        
        if not self._vector_store_initialized:
            try:
                get_vector_store()
                self._vector_store_initialized = True
            except Exception as e:
                logger.warning(f"向量数据库未初始化: {e}，尝试构建...")
                try:
                    build_vector_store()
                    self._vector_store_initialized = True
                except Exception as e2:
                    logger.error(f"无法初始化向量数据库: {e2}")
    
    def search(
        self,
        query: str,
        search_type: str = "hybrid",
        k: int = 5,
        book: Optional[str] = None,
        theme: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        搜索知识库
        
        Args:
            query: 查询文本
            search_type: 搜索类型 ('text', 'vector', 'hybrid')
            k: 返回结果数量
            book: 限制书籍（'素问' 或 '灵枢'）
            theme: 限制主题
            
        Returns:
            搜索结果
        """
        self.ensure_initialized()
        
        results = {
            'query': query,
            'text_results': [],
            'vector_results': [],
            'combined_results': [],
        }
        
        # 文本搜索（关键词匹配 + 可选主题）
        if search_type in ['text', 'hybrid']:
            try:
                text_results = text_search_by_keyword(query, self._structured_data)
                # 如果指定主题，同时合并主题文本搜索结果
                if theme:
                    theme_text_results = text_search_by_theme(theme, self._structured_data)
                    # 去重合并（按 书籍+标题）
                    seen_keys = set()
                    merged = []
                    for r in text_results + theme_text_results:
                        key = f"{r.get('book', '')}_{r.get('chapter_title', '')}"
                        if key not in seen_keys:
                            seen_keys.add(key)
                            merged.append(r)
                    text_results = merged
                results['text_results'] = text_results[:k]
            except Exception as e:
                logger.error(f"文本搜索失败: {e}")
        
        # 向量搜索（语义搜索）
        if search_type in ['vector', 'hybrid']:
            try:
                filter_dict = {}
                if book:
                    filter_dict['book'] = book
                # 为了提升混合检索的覆盖度，向量侧多取一些候选
                k_vec = max(k, k * 2)
                
                if filter_dict:
                    vector_results = similarity_search(query, k=k_vec, filter_dict=filter_dict)
                elif theme:
                    vector_results = vector_search_by_theme(query, theme, k=k_vec)
                else:
                    vector_results = similarity_search(query, k=k_vec)
                
                results['vector_results'] = vector_results
            except Exception as e:
                logger.error(f"向量搜索失败: {e}")
        
        # 合并结果（去重并排序）
        if search_type == 'hybrid':
            combined = {}
            text_raw_scores = {}
            text_len = len(results['text_results'])
            for i, result in enumerate(results['text_results']):
                key = f"{result.get('book', '')}_{result.get('chapter_title', '')}"
                if text_len <= 1:
                    raw = 1.0
                else:
                    raw = 1.0 - (i / (text_len - 1))
                text_raw_scores[key] = raw
                if key not in combined:
                    combined[key] = {
                        'type': 'text',
                        'book': result.get('book', ''),
                        'chapter_title': result.get('chapter_title', ''),
                        'content': result.get('content', ''),
                        'themes': result.get('themes', []),
                    }

            vec_raw_scores = {}
            for result in results['vector_results']:
                metadata = result.get('metadata', {})
                key = f"{metadata.get('book', '')}_{metadata.get('chapter_title', '')}"
                score = float(result.get('score', 0))
                raw_sim = 1.0 - score
                vec_raw_scores[key] = raw_sim
                if key not in combined:
                    # 向量结果优先回填整章内容
                    full = self.get_chapter_by_title(metadata.get('chapter_title', ''), metadata.get('book', ''))
                    full_content = full.get('content', '') if full else result.get('content', '')
                    combined[key] = {
                        'type': 'vector',
                        'book': metadata.get('book', ''),
                        'chapter_title': metadata.get('chapter_title', ''),
                        'content': full_content,
                        'themes': metadata.get('themes', '').split(',') if metadata.get('themes') else [],
                    }

            if text_raw_scores:
                t_min = min(text_raw_scores.values())
                t_max = max(text_raw_scores.values())
            else:
                t_min = 0.0
                t_max = 0.0
            if vec_raw_scores:
                v_min = min(vec_raw_scores.values())
                v_max = max(vec_raw_scores.values())
            else:
                v_min = 0.0
                v_max = 0.0

            def norm(v: float, lo: float, hi: float) -> float:
                if hi - lo <= 1e-12:
                    return 1.0 if hi > 0 else 0.0
                return (v - lo) / (hi - lo)

            w_text = 0.4
            w_vec = 0.6

            combined_list = []
            for key, item in combined.items():
                t = norm(text_raw_scores.get(key, 0.0), t_min, t_max) if text_raw_scores else 0.0
                v = norm(vec_raw_scores.get(key, 0.0), v_min, v_max) if vec_raw_scores else 0.0
                score = w_text * t + w_vec * v
                # 轻度加权：标题包含查询与主题命中
                try:
                    title = item.get('chapter_title', '') or ''
                    themes_list = item.get('themes', []) or []
                    if isinstance(themes_list, str):
                        themes_list = [themes_list]
                    if title and (str(query) in title):
                        score += 0.1
                    if theme and any(theme in th for th in themes_list):
                        score += 0.05
                except Exception:
                    pass
                if score > 1.0:
                    score = 1.0
                item_type = 'hybrid' if key in text_raw_scores and key in vec_raw_scores else item.get('type', 'text' if key in text_raw_scores else 'vector')
                combined_list.append({
                    **item,
                    'type': item_type,
                    'relevance_score': float(score),
                })

            results['combined_results'] = sorted(
                combined_list,
                key=lambda x: x['relevance_score'],
                reverse=True
            )[:k]
        
        return results
    
    def get_chapter_by_title(self, chapter_title: str, book: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        根据章节标题获取完整章节
        
        Args:
            chapter_title: 章节标题
            book: 书籍名称（可选）
            
        Returns:
            章节数据
        """
        self.ensure_initialized()
        
        for chapter in self._structured_data:
            if chapter_title in chapter.get('chapter_title', ''):
                if book is None or chapter.get('book') == book:
                    return chapter
        
        return None
    
    def get_chapters_by_theme(self, theme: str) -> List[Dict[str, Any]]:
        """
        根据主题获取章节列表
        
        Args:
            theme: 主题名称
            
        Returns:
            章节列表
        """
        self.ensure_initialized()
        return text_search_by_theme(theme, self._structured_data)
    
    def get_all_themes(self) -> List[str]:
        """
        获取所有主题列表
        
        Returns:
            主题列表
        """
        self.ensure_initialized()
        
        themes = set()
        for chapter in self._structured_data:
            themes.update(chapter.get('themes', []))
        
        return sorted(list(themes))
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取知识库统计信息
        
        Returns:
            统计信息
        """
        self.ensure_initialized()
        
        stats = {
            'total_chapters': len(self._structured_data),
            'suwen_count': sum(1 for ch in self._structured_data if ch.get('book') == '素问'),
            'lingshu_count': sum(1 for ch in self._structured_data if ch.get('book') == '灵枢'),
            'themes': {},
        }
        
        # 统计主题分布
        for chapter in self._structured_data:
            for theme in chapter.get('themes', []):
                if theme not in stats['themes']:
                    stats['themes'][theme] = 0
                stats['themes'][theme] += 1
        
        return stats


# 全局知识库实例（单例）
_knowledge_base: Optional[HuangdiKnowledgeBase] = None


def get_knowledge_base() -> HuangdiKnowledgeBase:
    """
    获取知识库实例（单例模式）
    
    Returns:
        知识库实例
    """
    global _knowledge_base
    if _knowledge_base is None:
        _knowledge_base = HuangdiKnowledgeBase()
    return _knowledge_base


if __name__ == "__main__":
    # 测试知识库
    logging.basicConfig(level=logging.INFO)
    
    kb = get_knowledge_base()
    
    # 测试搜索
    results = kb.search("什么是阴阳", search_type="hybrid", k=3)
    print(f"搜索结果: {len(results['combined_results'])} 条")
    for i, r in enumerate(results['combined_results'], 1):
        print(f"\n结果 {i}:")
        print(f"  来源: {r['chapter_title']}")
        print(f"  内容: {r['content'][:100]}...")
        print(f"  相关性: {r['relevance_score']:.4f}")
    
    # 测试统计
    stats = kb.get_statistics()
    print(f"\n知识库统计:")
    print(f"  总章节数: {stats['total_chapters']}")
    print(f"  素问: {stats['suwen_count']} 篇")
    print(f"  灵枢: {stats['lingshu_count']} 篇")
    print(f"  主题数: {len(stats['themes'])}")
