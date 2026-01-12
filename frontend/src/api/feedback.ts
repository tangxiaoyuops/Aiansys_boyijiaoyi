/**
 * 反馈功能API客户端
 * 包含需求提交、问题报告、打赏等功能
 */
import api from './index';

export interface RequirementRequest {
  title: string;
  content: string;
  contact?: string;
}

export interface RequirementResponse {
  id: number;
  title: string;
  content: string;
  contact?: string;
  status: string;
  created_at: string;
}

export interface IssueRequest {
  title: string;
  content: string;
  contact?: string;
  severity?: string; // low, medium, high, critical
}

export interface IssueResponse {
  id: number;
  title: string;
  content: string;
  contact?: string;
  severity: string;
  status: string;
  created_at: string;
}

export interface RewardRequest {
  amount: number;
  message?: string;
  contact?: string;
}

export interface RewardResponse {
  id: number;
  order_id: string;
  amount: number;
  message?: string;
  contact?: string;
  payment_status: string;
  payment_method?: string;
  created_at: string;
  paid_at?: string;
}

/**
 * 提交需求
 */
export async function submitRequirement(data: RequirementRequest): Promise<RequirementResponse> {
  const response = await api.post<RequirementResponse>('/api/requirements/submit', data);
  return response.data;
}

/**
 * 提交问题
 */
export async function submitIssue(data: IssueRequest): Promise<IssueResponse> {
  const response = await api.post<IssueResponse>('/api/issues/submit', data);
  return response.data;
}

/**
 * 创建打赏订单
 */
export async function createRewardOrder(data: RewardRequest): Promise<RewardResponse> {
  const response = await api.post<RewardResponse>('/api/rewards/create', data);
  return response.data;
}

/**
 * 执行支付（模拟支付）
 */
export async function payReward(orderId: string): Promise<{ success: boolean; order_id: string; status: string; message: string }> {
  const response = await api.post<{ success: boolean; order_id: string; status: string; message: string }>(`/api/rewards/pay/${orderId}`);
  return response.data;
}

/**
 * 查询订单状态
 */
export async function checkOrderStatus(orderId: string): Promise<RewardResponse> {
  const response = await api.get<RewardResponse>(`/api/rewards/status/${orderId}`);
  return response.data;
}

