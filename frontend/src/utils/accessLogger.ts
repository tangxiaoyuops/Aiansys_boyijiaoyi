/**
 * 前端访问日志工具
 * 记录页面访问、用户行为等日志到后端
 */
import axios from 'axios';

const API_BASE = '/api';

interface PageViewLog {
  page_name: string;
  user_info?: Record<string, any>;
  client_timestamp: string;
  current_path: string;
}

/**
 * 记录页面访问
 */
export async function logPageView(pageName: string, userInfo?: Record<string, any>): Promise<void> {
  try {
    const timestamp = getTimestamp();
    const data: PageViewLog = {
      page_name: pageName,
      user_info: userInfo,
      client_timestamp: timestamp,
      current_path: window.location.pathname
    };
    
    await axios.post(`${API_BASE}/log/page-view`, data);
    
    // 控制台也打印一份
    console.log(`[访问日志] ${timestamp} | 页面: ${pageName}`);
  } catch (error) {
    // 日志记录失败不影响主流程
    console.warn('[访问日志] 记录失败:', error);
  }
}

/**
 * 获取格式化时间戳
 */
export function getTimestamp(): string {
  const now = new Date();
  return now.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  });
}

/**
 * 本地日志打印（带时间戳）
 */
export function logLocal(message: string, data?: any): void {
  const timestamp = getTimestamp();
  if (data) {
    console.log(`[${timestamp}] ${message}`, data);
  } else {
    console.log(`[${timestamp}] ${message}`);
  }
}

/**
 * 记录用户操作
 */
export function logUserAction(action: string, details?: Record<string, any>): void {
  const timestamp = getTimestamp();
  console.log(`[${timestamp}] 用户操作: ${action}`, details || '');
}

/**
 * 记录API调用
 */
export function logApiCall(apiName: string, params?: any, responseTime?: number): void {
  const timestamp = getTimestamp();
  const timeStr = responseTime ? ` | 耗时: ${responseTime}ms` : '';
  console.log(`[${timestamp}] API调用: ${apiName}${timeStr}`, params || '');
}

export default {
  logPageView,
  logLocal,
  logUserAction,
  logApiCall
};
