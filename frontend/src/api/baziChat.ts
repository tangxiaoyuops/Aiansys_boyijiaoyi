import { API_BASE_URL } from './index';

export interface BaziChatPayload {
  message: string;
  conversation_id?: string | null;
  name?: string;  // 姓名（可选）
  sizhu?: Record<string, any> | null;
  wuxing_analysis?: Record<string, any> | null;
  shishen_analysis?: Record<string, any> | null;
  dayun_analysis?: Record<string, any> | null;
  liunian_analysis?: Record<string, any> | null;
  shensha_analysis?: Record<string, any> | null;
  llm_analysis?: string | null;
  analysis_style?: string;
  gender?: string;
  birth_info?: Record<string, any> | null;
}

export interface SSEEvent {
  type: string;
  [key: string]: any;
}

export type SSEEventHandler = (event: SSEEvent) => void;
export type ErrorHandler = (error: Error) => void;

/**
 * 八字追问流式对话
 */
export function startBaziChatStream(
  payload: BaziChatPayload,
  onEvent: SSEEventHandler,
  onError?: ErrorHandler
): () => void {
  const controller = new AbortController();
  
  const runStream = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/bazi/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
        },
        body: JSON.stringify(payload),
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      if (!response.body) {
        throw new Error('Response body is null');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        const parts = buffer.split('\n\n');
        buffer = parts.pop() || '';

        for (const part of parts) {
          const line = part.trim();
          if (!line.startsWith('data:')) continue;
          
          const jsonStr = line.slice(5).trim();
          if (!jsonStr) continue;

          try {
            const event = JSON.parse(jsonStr) as SSEEvent;
            onEvent(event);
          } catch (parseError) {
            console.warn('Failed to parse SSE event:', jsonStr, parseError);
          }
        }
      }

      if (buffer.trim()) {
        const line = buffer.trim();
        if (line.startsWith('data:')) {
          const jsonStr = line.slice(5).trim();
          if (jsonStr) {
            try {
              const event = JSON.parse(jsonStr) as SSEEvent;
              onEvent(event);
            } catch (parseError) {
              console.warn('Failed to parse remaining SSE event:', jsonStr, parseError);
            }
          }
        }
      }
    } catch (error) {
      if ((error as Error).name === 'AbortError') {
        return;
      }
      console.error('SSE stream error:', error);
      if (onError) {
        onError(error as Error);
      }
    }
  };

  runStream();

  return () => {
    controller.abort();
  };
}

/**
 * 八字追问非流式对话
 */
export async function baziChat(payload: BaziChatPayload): Promise<{
  success: boolean;
  conversation_id: string;
  response: string;
}> {
  const response = await fetch(`${API_BASE_URL}/api/bazi/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
}

/**
 * 获取八字对话历史
 */
export async function getBaziChatHistory(conversationId: string): Promise<{
  success: boolean;
  conversation_id: string;
  history: Array<{ role: string; content: string }>;
}> {
  const response = await fetch(
    `${API_BASE_URL}/api/bazi/chat/history/${conversationId}`
  );

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
}

/**
 * 清除八字对话历史
 */
export async function clearBaziChatHistory(conversationId: string): Promise<{
  success: boolean;
  message: string;
}> {
  const response = await fetch(
    `${API_BASE_URL}/api/bazi/chat/history/${conversationId}`,
    {
      method: 'DELETE',
    }
  );

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
}

// ==================== 合盘对话 API ====================

export interface HepanChatPayload {
  message: string;
  conversation_id?: string | null;
  hepan_type?: 'couple' | 'business';
  // 命盘A
  name_a?: string;  // 姓名（可选）
  pan_a?: Record<string, any> | null;
  birth_info_a?: Record<string, any> | null;
  gender_a?: string;
  // 命盘B
  name_b?: string;  // 姓名（可选）
  pan_b?: Record<string, any> | null;
  birth_info_b?: Record<string, any> | null;
  gender_b?: string;
  // 合盘结果
  hepan_result?: Record<string, any> | null;
  llm_analysis?: string | null;
  // 历史消息
  chat_history?: Array<{ role: string; content: string; type?: string }>;
}

/**
 * 合盘追问流式对话
 */
export function startHepanChatStream(
  payload: HepanChatPayload,
  onEvent: SSEEventHandler,
  onError?: ErrorHandler
): () => void {
  const controller = new AbortController();
  
  const runStream = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/bazi/hepan-chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
        },
        body: JSON.stringify(payload),
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      if (!response.body) {
        throw new Error('Response body is null');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        const parts = buffer.split('\n\n');
        buffer = parts.pop() || '';

        for (const part of parts) {
          const line = part.trim();
          if (!line.startsWith('data:')) continue;
          
          const jsonStr = line.slice(5).trim();
          if (!jsonStr) continue;

          try {
            const event = JSON.parse(jsonStr) as SSEEvent;
            onEvent(event);
          } catch (parseError) {
            console.warn('Failed to parse SSE event:', jsonStr, parseError);
          }
        }
      }

      if (buffer.trim()) {
        const line = buffer.trim();
        if (line.startsWith('data:')) {
          const jsonStr = line.slice(5).trim();
          if (jsonStr) {
            try {
              const event = JSON.parse(jsonStr) as SSEEvent;
              onEvent(event);
            } catch (parseError) {
              console.warn('Failed to parse remaining SSE event:', jsonStr, parseError);
            }
          }
        }
      }
    } catch (error) {
      if ((error as Error).name === 'AbortError') {
        return;
      }
      console.error('SSE stream error:', error);
      if (onError) {
        onError(error as Error);
      }
    }
  };

  runStream();

  return () => {
    controller.abort();
  };
}

/**
 * 合盘追问非流式对话
 */
export async function hepanChat(payload: HepanChatPayload): Promise<{
  success: boolean;
  conversation_id: string;
  response: string;
}> {
  const response = await fetch(`${API_BASE_URL}/api/bazi/hepan-chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
}