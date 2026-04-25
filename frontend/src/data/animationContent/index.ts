/**
 * 动画内容索引文件
 * 新增内容请在此文件中导出
 */
import { AnimationContent, ContentType } from '@/types/animation';

// 导入各个内容模块
import { jianLaiQuotes } from './jianlai_quotes';

/** 所有动画内容列表 */
export const allContent: AnimationContent[] = [
  jianLaiQuotes
];

/** 按类型获取内容 */
export function getContentByType(type: ContentType): AnimationContent[] {
  return allContent.filter(item => item.type === type);
}

/** 按ID获取内容 */
export function getContentById(id: string): AnimationContent | undefined {
  return allContent.find(item => item.id === id);
}

/** 获取推荐内容（随机排序） */
export function getRecommendedContent(count: number = 4): AnimationContent[] {
  const shuffled = [...allContent].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, count);
}

/** 搜索内容 */
export function searchContent(keyword: string): AnimationContent[] {
  const lowerKeyword = keyword.toLowerCase();
  return allContent.filter(item => 
    item.title.toLowerCase().includes(lowerKeyword) ||
    item.subtitle?.toLowerCase().includes(lowerKeyword) ||
    item.tags?.some(tag => tag.toLowerCase().includes(lowerKeyword))
  );
}

// 导出各个内容模块
export {
  jianLaiQuotes
};

export default allContent;
