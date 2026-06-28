import { API_BASE_URL } from './index';

export interface ZiweiChatPayload {
  message: string;
  conversation_id?: string | null;
  // 紫薇斗数上下文
  pan_data?: Record<string, any> | null;
  si_hua_analysis?: Record<string, any> | null;
  daxian_analysis?: Record<string, any> | null;
  liunian_analysis?: Record<string, any> | null;
  shensha_analysis?: Record<string, any> | null;
  geju_analysis?: Record<string, any> | null;
  llm_analysis?: string | null;
  gender?: string;
  birth_info?: Record<string, any> | null;
  // 历史消息
  chat_history?: Array<{ role: string; content: string; type?: string }>;
}

export interface SSEEvent {
  type: string;
  [key: string]: any;
}

export type SSEEventHandler = (event: SSEEvent) => void;
export type ErrorHandler = (error: Error) => void;

/**
 * 紫薇斗数追问流式对话
 */
export function startZiweiChatStream(
  payload: ZiweiChatPayload,
  onEvent: SSEEventHandler,
  onError?: ErrorHandler
): () => void {
  const controller = new AbortController();
  
  const runStream = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/ziwei/chat/stream`, {
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
 * 紫薇斗数追问非流式对话
 */
export async function ziweiChat(payload: ZiweiChatPayload): Promise<{
  success: boolean;
  conversation_id: string;
  response: string;
}> {
  const response = await fetch(`${API_BASE_URL}/api/ziwei/chat`, {
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
 * 清除紫薇对话历史
 */
export async function clearZiweiChatHistory(conversationId: string): Promise<{
  success: boolean;
  message: string;
}> {
  const response = await fetch(
    `${API_BASE_URL}/api/ziwei/chat/history/${conversationId}`,
    {
      method: 'DELETE',
    }
  );

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
}