import api from './index';

export interface OCRUploadResponse {
  success: boolean;
  image_id: string;
  filename: string;
  file_size: number;
  preview_url: string;
}

export interface OCRRecognizeRequest {
  image_id?: string;
  context?: string;
}

export interface OCRRecognizeResponse {
  success: boolean;
  text: string;
  image_id?: string;
  model?: string;
  elapsed_time?: number;
  error?: string;
}

/**
 * 上传图片
 */
export const uploadImage = async (file: File): Promise<OCRUploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post<OCRUploadResponse>('/api/ocr/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

/**
 * 识别图片文字
 */
export const recognizeImage = async (
  request: OCRRecognizeRequest,
  file?: File
): Promise<OCRRecognizeResponse> => {
  if (file) {
    // 直接上传图片并识别
    const formData = new FormData();
    formData.append('file', file);
    // 注意：FastAPI的FormData需要单独处理，不能直接传JSON
    // 这里我们需要通过查询参数或FormData字段传递context
    const params: any = {};
    if (request.context) {
      params.context = request.context;
    }

    const response = await api.post<OCRRecognizeResponse>(
      '/api/ocr/recognize',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        params: params,
      }
    );

    return response.data;
  } else if (request.image_id) {
    // 通过image_id识别
    const response = await api.post<OCRRecognizeResponse>('/api/ocr/recognize', {
      image_id: request.image_id,
      context: request.context || '',
    });

    return response.data;
  } else {
    throw new Error('请提供image_id或上传图片文件');
  }
};

/**
 * OCR+分析（股票分析场景）
 */
export const analyzeImage = async (
  request: OCRRecognizeRequest,
  file?: File
): Promise<OCRRecognizeResponse> => {
  if (file) {
    // 直接上传图片并分析
    const formData = new FormData();
    formData.append('file', file);
    const params: any = {};
    if (request.context) {
      params.context = request.context;
    }

    const response = await api.post<OCRRecognizeResponse>(
      '/api/ocr/analyze',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        params: params,
      }
    );

    return response.data;
  } else if (request.image_id) {
    // 通过image_id分析
    const response = await api.post<OCRRecognizeResponse>('/api/ocr/analyze', {
      image_id: request.image_id,
      context: request.context || '',
    });

    return response.data;
  } else {
    throw new Error('请提供image_id或上传图片文件');
  }
};

/**
 * 获取图片预览URL
 */
export const getImagePreviewUrl = (imageId: string): string => {
  const baseURL = import.meta.env.VITE_API_BASE || 'http://localhost:8000';
  return `${baseURL}/api/ocr/preview/${imageId}`;
};

