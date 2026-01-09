"""
黄帝内经文本处理工具
解析文本，识别章节结构，提取关键信息，生成结构化数据
"""
import os
import json
import re
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "huangdi_neijing", "raw")
STRUCTURED_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "huangdi_neijing", "structured")

# 主题分类关键词
THEME_KEYWORDS = {
    "阴阳五行": ["阴阳", "五行", "金木水火土", "天地", "乾坤"],
    "脏腑经络": ["五脏", "六腑", "经络", "经脉", "脏腑", "心肝脾肺肾", "胆胃大肠小肠膀胱三焦"],
    "病因病机": ["病因", "病机", "邪气", "正气", "虚实", "寒热", "表里"],
    "诊断": ["诊", "望", "闻", "问", "切", "脉", "色", "形"],
    "治疗": ["治", "疗", "针", "灸", "药", "方", "补", "泻"],
    "养生": ["养", "生", "四时", "起居", "饮食", "情志", "导引", "吐纳"],
}


def parse_text_file(file_path: str) -> List[Dict[str, Any]]:
    """
    解析文本文件，提取章节结构
    
    Args:
        file_path: 文本文件路径
        
    Returns:
        结构化数据列表
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 确定是素问还是灵枢
        book_name = "素问" if "素问" in os.path.basename(file_path) else "灵枢"
        
        # 解析章节
        chapters = []
        lines = content.split('\n')
        current_chapter = None
        current_section = None
        text_buffer = []
        
        for line in lines:
            line_original = line
            line = line.strip()
            if not line:
                continue
            
            # 匹配篇名（如"第一篇 上古天真论"或"## 第一篇 上古天真论"）
            # 先处理以#开头的行
            line_for_match = line
            if line.startswith('#'):
                # 移除开头的#号
                line_for_match = re.sub(r'^#+\s*', '', line)
            
            chapter_match = re.match(r'^第?([一二三四五六七八九十百千万]+|[0-9]+)[篇章]\s*(.+?)$', line_for_match)
            if chapter_match:
                # 保存上一章节
                if current_chapter:
                    current_chapter['content'] = '\n'.join(text_buffer)
                    chapters.append(current_chapter)
                
                # 开始新章节
                chapter_num = chapter_match.group(1)
                chapter_title = chapter_match.group(2).strip()
                current_chapter = {
                    'book': book_name,
                    'chapter_number': chapter_num,
                    'chapter_title': chapter_title,
                    'sections': [],
                    'content': '',
                    'themes': [],
                }
                text_buffer = []
                current_section = None
                continue
            
            # 匹配章节名（如"## 第二篇 四气调神大论"）
            section_match = re.match(r'^#+\s*(.+?)$', line)
            if section_match and current_chapter:
                section_title = section_match.group(1).strip()
                if section_title != current_chapter.get('chapter_title'):
                    current_section = {
                        'title': section_title,
                        'content': '',
                    }
                    current_chapter['sections'].append(current_section)
                continue
            
            # 收集文本内容
            if line:
                text_buffer.append(line)
                if current_section:
                    current_section['content'] += line + '\n'
        
        # 保存最后一个章节
        if current_chapter:
            current_chapter['content'] = '\n'.join(text_buffer)
            chapters.append(current_chapter)
        
        # 识别主题
        for chapter in chapters:
            chapter['themes'] = identify_themes(chapter['content'])
        
        return chapters
        
    except Exception as e:
        logger.error(f"解析文件失败: {file_path}, 错误: {e}")
        return []


def identify_themes(text: str) -> List[str]:
    """
    识别文本主题
    
    Args:
        text: 文本内容
        
    Returns:
        主题列表
    """
    themes = []
    text_lower = text.lower()
    
    for theme, keywords in THEME_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                if theme not in themes:
                    themes.append(theme)
                break
    
    return themes


def process_all_files() -> Dict[str, Any]:
    """
    处理所有原始文本文件，生成结构化数据
    
    Returns:
        处理结果
    """
    # 确保输出目录存在
    os.makedirs(STRUCTURED_DATA_DIR, exist_ok=True)
    
    all_chapters = []
    
    # 处理素问
    suwen_path = os.path.join(RAW_DATA_DIR, "suwen.txt")
    if not os.path.exists(suwen_path):
        # 尝试使用示例文件
        suwen_path = os.path.join(RAW_DATA_DIR, "suwen_sample.txt")
    
    if os.path.exists(suwen_path):
        logger.info(f"处理素问文件: {suwen_path}")
        suwen_chapters = parse_text_file(suwen_path)
        all_chapters.extend(suwen_chapters)
        logger.info(f"素问解析完成，共 {len(suwen_chapters)} 篇")
    
    # 处理灵枢
    lingshu_path = os.path.join(RAW_DATA_DIR, "lingshu.txt")
    if not os.path.exists(lingshu_path):
        # 尝试使用示例文件
        lingshu_path = os.path.join(RAW_DATA_DIR, "lingshu_sample.txt")
    
    if os.path.exists(lingshu_path):
        logger.info(f"处理灵枢文件: {lingshu_path}")
        lingshu_chapters = parse_text_file(lingshu_path)
        all_chapters.extend(lingshu_chapters)
        logger.info(f"灵枢解析完成，共 {len(lingshu_chapters)} 篇")
    
    # 保存结构化数据
    output_file = os.path.join(STRUCTURED_DATA_DIR, "chapters.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_chapters, f, ensure_ascii=False, indent=2)
    
    logger.info(f"结构化数据已保存到: {output_file}")
    
    # 生成索引文件
    index_data = {
        'total_chapters': len(all_chapters),
        'suwen_count': sum(1 for ch in all_chapters if ch['book'] == '素问'),
        'lingshu_count': sum(1 for ch in all_chapters if ch['book'] == '灵枢'),
        'themes': {},
    }
    
    # 统计主题分布
    for chapter in all_chapters:
        for theme in chapter.get('themes', []):
            if theme not in index_data['themes']:
                index_data['themes'][theme] = 0
            index_data['themes'][theme] += 1
    
    index_file = os.path.join(STRUCTURED_DATA_DIR, "index.json")
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"索引文件已保存到: {index_file}")
    
    return {
        'success': True,
        'total_chapters': len(all_chapters),
        'output_file': output_file,
        'index_file': index_file,
    }


def load_structured_data() -> List[Dict[str, Any]]:
    """
    加载结构化数据
    
    Returns:
        章节列表
    """
    chapters_file = os.path.join(STRUCTURED_DATA_DIR, "chapters.json")
    if not os.path.exists(chapters_file):
        logger.warning(f"结构化数据文件不存在: {chapters_file}，尝试重新处理...")
        process_all_files()
    
    try:
        with open(chapters_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"加载结构化数据失败: {e}")
        return []


def search_by_keyword(keyword: str, chapters: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """
    根据关键词搜索章节
    
    Args:
        keyword: 搜索关键词
        chapters: 章节列表，如果为None则自动加载
        
    Returns:
        匹配的章节列表
    """
    if chapters is None:
        chapters = load_structured_data()
    
    results = []
    keyword_lower = keyword.lower()
    
    for chapter in chapters:
        # 搜索标题和内容
        if (keyword_lower in chapter.get('chapter_title', '').lower() or
            keyword_lower in chapter.get('content', '').lower()):
            results.append(chapter)
    
    return results


def search_by_theme(theme: str, chapters: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """
    根据主题搜索章节
    
    Args:
        theme: 主题名称
        chapters: 章节列表，如果为None则自动加载
        
    Returns:
        匹配的章节列表
    """
    if chapters is None:
        chapters = load_structured_data()
    
    results = []
    
    for chapter in chapters:
        if theme in chapter.get('themes', []):
            results.append(chapter)
    
    return results


if __name__ == "__main__":
    # 测试处理
    logging.basicConfig(level=logging.INFO)
    result = process_all_files()
    print(f"处理完成: {result}")
