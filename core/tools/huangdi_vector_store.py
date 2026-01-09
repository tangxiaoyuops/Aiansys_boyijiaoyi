"""
黄帝内经向量存储工具
使用ChromaDB存储文本向量，支持语义搜索
"""
import os
import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
from langchain.text_splitter import RecursiveCharacterTextSplitter
try:
    # 新版本LangChain
    from langchain_openai import OpenAIEmbeddings
    from langchain_community.vectorstores import Chroma
    from langchain_core.documents import Document
except ImportError:
    # 旧版本LangChain
    try:
        from langchain.embeddings import OpenAIEmbeddings
        from langchain.vectorstores import Chroma
        from langchain.schema import Document
    except ImportError:
        try:
            from langchain_openai import OpenAIEmbeddings
            from langchain_community.vectorstores import Chroma
            from langchain_core.documents import Document
        except ImportError:
            # 最后尝试
            from langchain.embeddings.openai import OpenAIEmbeddings
            from langchain.vectorstores import Chroma
            from langchain.schema import Document

from core.tools.huangdi_text_processor import load_structured_data
from core.tools.qwen_embeddings import QwenEmbeddings

logger = logging.getLogger(__name__)

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VECTOR_DB_DIR = os.path.join(PROJECT_ROOT, "data", "huangdi_neijing", "vector_db")

# 全局变量
_vector_store: Optional[Chroma] = None
_embeddings: Optional[Any] = None  # 可能是OpenAIEmbeddings或QwenEmbeddings


def get_embeddings():
    """
    获取Embeddings实例（单例模式）
    优先使用千问的embedding模型
    
    Returns:
        OpenAIEmbeddings实例
    """
    global _embeddings
    if _embeddings is None:
        # 使用千问的embedding模型（通过OpenAI兼容接口）
        api_key = os.getenv("OPENAI_API_KEY", "sk-704557ba3af94909ab21294bc4792a6c")
        base_url = os.getenv("OPENAI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        
        # 千问的embedding模型名称
        # 千问在dashscope中通常使用 text-embedding-v1 或 text-embedding-v2
        # 如果使用OpenAI兼容接口，可能需要使用 text-embedding-v2
        embedding_model = os.getenv("QWEN_EMBEDDING_MODEL", "text-embedding-v2")
        
        if not api_key:
            raise ValueError(
                "未找到OPENAI_API_KEY环境变量！\n"
                "请设置环境变量或在.env文件中配置：\n"
                "OPENAI_API_KEY=your_qwen_api_key\n"
                "OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1 (可选)\n"
                "QWEN_EMBEDDING_MODEL=text-embedding-v2 (可选)"
            )
        
        logger.info(f"使用千问Embedding模型: {embedding_model}")
        logger.info(f"API Base URL: {base_url}")
        logger.info(f"API Key: {'*' * 10 + api_key[-4:] if len(api_key) > 4 else '***'}")
        
        # 使用千问Embedding适配器（直接调用API，避免格式问题）
        try:
            logger.info("使用千问Embedding适配器...")
            _embeddings = QwenEmbeddings(
                api_key=api_key,
                base_url=base_url,
                model=embedding_model,
            )
            logger.info("✓ 千问Embedding适配器初始化成功")
        except Exception as e:
            error_msg = str(e)
            logger.error(f"千问Embedding适配器初始化失败: {error_msg}")
            # 如果适配器失败，尝试直接使用OpenAIEmbeddings（可能格式已兼容）
            logger.info("尝试直接使用OpenAIEmbeddings...")
            try:
                _embeddings = OpenAIEmbeddings(
                    openai_api_key=api_key,
                    openai_api_base=base_url,
                    model=embedding_model,
                )
                logger.info("✓ 直接使用OpenAIEmbeddings成功")
            except Exception as e2:
                raise ValueError(
                    f"千问Embedding初始化失败！\n"
                    f"适配器错误: {error_msg}\n"
                    f"直接调用错误: {e2}\n\n"
                    "请检查：\n"
                    "1. OPENAI_API_KEY是否正确\n"
                    "2. OPENAI_BASE_URL是否正确\n"
                    "3. API key是否有足够的余额和权限\n"
                    "4. 可以尝试设置 QWEN_EMBEDDING_MODEL 环境变量指定模型名称"
                )
    
    return _embeddings


def get_vector_store(recreate: bool = False) -> Chroma:
    """
    获取向量存储实例（单例模式）
    
    Args:
        recreate: 是否重新创建向量数据库
        
    Returns:
        Chroma向量存储实例
    """
    global _vector_store
    
    if _vector_store is not None and not recreate:
        return _vector_store
    
    # 确保目录存在
    os.makedirs(VECTOR_DB_DIR, exist_ok=True)
    
    embeddings = get_embeddings()
    
    # 检查是否已存在向量数据库
    persist_directory = os.path.join(VECTOR_DB_DIR, "chroma_db")
    
    if os.path.exists(persist_directory) and os.listdir(persist_directory) and not recreate:
        logger.info(f"加载现有向量数据库: {persist_directory}")
        _vector_store = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings,
        )
    else:
        logger.info("创建新的向量数据库（空数据库，需要调用build_vector_store初始化数据）...")
        # 创建新的向量数据库（空数据库，数据由build_vector_store添加）
        _vector_store = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings,
        )
    
    return _vector_store


def build_vector_store() -> Dict[str, Any]:
    """
    构建向量数据库，从结构化数据中加载文本并向量化
    
    Returns:
        构建结果
    """
    logger.info("开始构建向量数据库...")
    
    # 加载结构化数据
    chapters = load_structured_data()
    if not chapters:
        logger.warning("没有找到结构化数据，先处理文本文件...")
        from core.tools.huangdi_text_processor import process_all_files
        process_all_files()
        chapters = load_structured_data()
    
    if not chapters:
        raise ValueError("无法加载结构化数据")
    
    # 创建文档列表
    documents = []
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,  # 每个chunk约500字符
        chunk_overlap=50,  # 重叠50字符
        length_function=len,
    )
    
    for chapter in chapters:
        # 为每个章节创建文档
        chapter_text = f"【{chapter['book']}】{chapter['chapter_title']}\n\n{chapter['content']}"
        
        # 分割文本
        chunks = text_splitter.split_text(chapter_text)
        
        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk,
                metadata={
                    'book': chapter['book'],
                    'chapter_number': chapter.get('chapter_number', ''),
                    'chapter_title': chapter['chapter_title'],
                    'chunk_index': i,
                    'themes': ','.join(chapter.get('themes', [])),
                }
            )
            documents.append(doc)
    
    logger.info(f"共创建 {len(documents)} 个文档块")
    
    # 获取向量存储（重新创建）
    embeddings = get_embeddings()
    persist_directory = os.path.join(VECTOR_DB_DIR, "chroma_db")
    
    # 删除旧数据库（如果存在）
    import shutil
    if os.path.exists(persist_directory):
        shutil.rmtree(persist_directory)
    
    # 创建新的向量数据库
    vector_store = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings,
    )
    
    # 添加文档到向量数据库
    if documents:
        vector_store.add_documents(documents)
        vector_store.persist()
        logger.info(f"向量数据库构建完成，共 {len(documents)} 个文档块")
    
    # 更新全局变量
    global _vector_store
    _vector_store = vector_store
    
    return {
        'success': True,
        'total_chunks': len(documents),
        'total_chapters': len(chapters),
    }


def similarity_search(
    query: str,
    k: int = 5,
    filter_dict: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    语义搜索
    
    Args:
        query: 查询文本
        k: 返回结果数量
        filter_dict: 过滤条件（如 {'book': '素问'}）
        
    Returns:
        搜索结果列表
    """
    vector_store = get_vector_store()
    
    # 执行搜索
    if filter_dict:
        # 使用where条件过滤
        results = vector_store.similarity_search_with_score(
            query,
            k=k,
            where=filter_dict
        )
    else:
        results = vector_store.similarity_search_with_score(query, k=k)
    
    # 格式化结果
    formatted_results = []
    for doc, score in results:
        formatted_results.append({
            'content': doc.page_content,
            'metadata': doc.metadata,
            'score': float(score),
        })
    
    return formatted_results


def search_by_book(query: str, book: str, k: int = 5) -> List[Dict[str, Any]]:
    """
    在指定书籍中搜索
    
    Args:
        query: 查询文本
        book: 书籍名称（'素问' 或 '灵枢'）
        k: 返回结果数量
        
    Returns:
        搜索结果列表
    """
    return similarity_search(query, k=k, filter_dict={'book': book})


def search_by_theme(query: str, theme: str, k: int = 5) -> List[Dict[str, Any]]:
    """
    在指定主题中搜索
    
    Args:
        query: 查询文本
        theme: 主题名称
        k: 返回结果数量
        
    Returns:
        搜索结果列表
    """
    # 注意：ChromaDB的where条件不支持部分匹配，所以我们需要先搜索，然后过滤
    results = similarity_search(query, k=k * 2)  # 多取一些结果
    
    # 过滤主题
    filtered_results = [
        r for r in results
        if theme in r['metadata'].get('themes', '')
    ]
    
    return filtered_results[:k]


if __name__ == "__main__":
    # 测试向量存储
    logging.basicConfig(level=logging.INFO)
    
    # 构建向量数据库
    result = build_vector_store()
    print(f"构建结果: {result}")
    
    # 测试搜索
    test_query = "什么是阴阳"
    results = similarity_search(test_query, k=3)
    print(f"\n查询: {test_query}")
    for i, r in enumerate(results, 1):
        print(f"\n结果 {i}:")
        print(f"  内容: {r['content'][:100]}...")
        print(f"  来源: {r['metadata']['chapter_title']}")
        print(f"  相似度: {r['score']:.4f}")
