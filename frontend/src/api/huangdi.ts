import { api } from './index';

/**
 * 黄帝内经API接口
 */

export interface HuangdiRequest {
  question: string;
  query_type?: 'query' | 'diagnosis' | 'consultation';
  include_llm?: boolean;
  context?: {
    season?: string;
    age?: number;
    constitution?: string[];
  };
}

export interface HuangdiQueryResponse {
  success: boolean;
  query_type: 'query';
  question: string;
  relevant_chapters: Array<{
    book: string;
    chapter_title: string;
    content: string;
    relevance_score: number;
    themes: string[];
  }>;
  llm_explanation?: string;
  total_results: number;
}

export interface HuangdiDiagnosisResponse {
  success: boolean;
  query_type: 'diagnosis';
  question: string;
  symptoms: string;
  symptom_keywords: string[];
  relevant_theories: Array<{
    book: string;
    chapter_title: string;
    content: string;
    relevance_score: number;
  }>;
  llm_analysis?: string;
  disclaimer: string;
}

export interface HuangdiConsultationResponse {
  success: boolean;
  query_type: 'consultation';
  question: string;
  season?: string;
  age?: number;
  constitution: string[];
  relevant_theories: Array<{
    book: string;
    chapter_title: string;
    content: string;
    relevance_score: number;
  }>;
  llm_suggestions?: string;
  disclaimer: string;
}

export type HuangdiResponse = 
  | HuangdiQueryResponse 
  | HuangdiDiagnosisResponse 
  | HuangdiConsultationResponse;

/**
 * 黄帝内经分析接口
 */
export function huangdiAnalyze(payload: HuangdiRequest) {
  return api.post<HuangdiResponse>('/api/huangdi/analyze', payload);
}

/**
 * 测试API是否可用
 */
export function huangdiTest() {
  return api.get('/api/huangdi/test');
}

