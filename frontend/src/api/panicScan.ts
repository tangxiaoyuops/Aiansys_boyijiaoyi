/**
 * 恐慌点扫描相关API
 */
import axios from 'axios';
import { API_BASE_URL } from './index';

export interface PanicScanRecord {
  code: string;
  name: string;
  panic_date: string;
  panic_type: string;
  panic_desc: string;
  drop_pct: number;
  vol_ratio: number;
  score: number;
  current_price: number;
  ma60?: number;
  over_ma60_pct?: number;
  recent_gain_20d?: number;
}

export interface ScanFile {
  filename: string;
  date: string;
  type: string;
  size: number;
}

export interface ScanResult {
  success: boolean;
  date?: string;
  filename?: string;
  count?: number;
  records?: PanicScanRecord[];
  files?: ScanFile[];
  message?: string;
}

/**
 * 列出所有扫描结果文件
 */
export async function listScanResults(): Promise<ScanResult> {
  const response = await axios.get(`${API_BASE_URL}/api/panic-scan/list`);
  return response.data;
}

/**
 * 获取最新的扫描结果
 */
export async function getLatestScanResult(): Promise<ScanResult> {
  const response = await axios.get(`${API_BASE_URL}/api/panic-scan/latest`);
  return response.data;
}

/**
 * 根据日期获取扫描结果
 */
export async function getScanResultByDate(date: string): Promise<ScanResult> {
  const response = await axios.get(`${API_BASE_URL}/api/panic-scan/by-date/${date}`);
  return response.data;
}

/**
 * 触发一次扫描
 */
export async function triggerScan(params: {
  days?: number;
  panic_window?: number;
  recent_days?: number;
  top_k?: number;
}): Promise<{ success: boolean; message: string; pid?: number }> {
  const response = await axios.post(`${API_BASE_URL}/api/panic-scan/trigger`, params);
  return response.data;
}

