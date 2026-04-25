/**
 * 动画演示模块类型定义
 */

/** 内容类型枚举 */
export enum ContentType {
  READING = 'reading',      // 读书分享
  THINKING = 'thinking',    // 思维升华
  KNOWLEDGE = 'knowledge',  // 知识科普
  WISDOM = 'wisdom',        // 哲理故事
  DAILY = 'daily'           // 每日一签
}

/** 内容类型显示名称 */
export const ContentTypeLabels: Record<ContentType, string> = {
  [ContentType.READING]: '读书分享',
  [ContentType.THINKING]: '思维升华',
  [ContentType.KNOWLEDGE]: '知识科普',
  [ContentType.WISDOM]: '哲理故事',
  [ContentType.DAILY]: '每日一签'
};

/** 动画效果类型 */
export enum AnimationType {
  TYPEWRITER = 'typewriter',    // 打字机
  FADE_IN = 'fadeIn',           // 淡入
  SLIDE_UP = 'slideUp',         // 上滑
  SLIDE_LEFT = 'slideLeft',     // 左滑
  BOUNCE = 'bounce',            // 弹跳
  FLIP = 'flip',                // 翻转
  ZOOM = 'zoom',                // 缩放
  PARTICLE = 'particle'         // 粒子
}

/** 场景类型 */
export type SceneType = 'text' | 'image' | 'quote' | 'list' | 'card' | 'title';

/** 场景样式 */
export interface SceneStyle {
  fontSize?: string;
  color?: string;
  textAlign?: 'left' | 'center' | 'right';
  fontWeight?: string;
  background?: string;
  paddingTop?: string;
  paddingBottom?: string;
}

/** 单个场景 */
export interface Scene {
  id: string;
  type: SceneType;
  content: string | string[];
  animation: AnimationType;
  duration: number;          // 毫秒
  delay?: number;            // 延迟
  style?: SceneStyle;
}

/** 渐变背景配置 */
export interface GradientConfig {
  colors: string[];
  angle?: number;
  animated?: boolean;
}

/** 背景配置 */
export interface BackgroundConfig {
  type: 'gradient' | 'particle' | 'image' | 'solid' | 'snow';
  value: string | GradientConfig;
}

/** 动画内容 */
export interface AnimationContent {
  id: string;
  title: string;
  subtitle?: string;
  type: ContentType;
  thumbnail?: string;
  duration: number;          // 总时长(秒)
  author?: string;
  source?: string;
  tags?: string[];
  scenes: Scene[];
  background: BackgroundConfig;
  createdAt: string;
  updatedAt: string;
}

/** 播放状态 */
export type PlayStatus = 'idle' | 'playing' | 'paused' | 'ended';
